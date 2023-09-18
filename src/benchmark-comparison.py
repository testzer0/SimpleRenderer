import numpy as np
import os
import renderer
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import PIL
import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Pango, PangoCairo
from time import time
import pygame
import cairo

import sys
sys.path = sys.path[:-1]
pygame.init()

s = open("../../screenshotlm/tmp/text512256br").read()

def get_unrendered(paragraphs, p_idx, w_idx, return_unrendered, is_text_wrap_overflow):
    if (not return_unrendered) or (return_unrendered and p_idx == len(paragraphs)):
        return None
    else:
        unrendered = ''
        unrendered += ' '.join(paragraphs[p_idx][w_idx:]) + '\n' \
                    if w_idx < len(paragraphs[p_idx]) and is_text_wrap_overflow else ''
        p_idx += 1
        while p_idx < len(paragraphs):
            unrendered += ' '.join(paragraphs[p_idx]) + '\n'
            p_idx += 1
        return unrendered if unrendered != '' else None

# code mostly adapted from https://stackoverflow.com/questions/42014195/rendering-text-with-multiple-lines-in-pygame 
def blit_text(surface, text, pos, font, 
              color, return_unrendered, alt_space_width, antialias,
              line_space_scale, paragraph_space_scale):
    # 2d list of (paragraph, word)
    paragraphs = [paragraph.split(' ') for paragraph in text.splitlines()]
    # The width of a space.
    space_width = font.size(' ')[0] if alt_space_width is None else alt_space_width
    max_width, max_height = surface.get_size()
    x, y = pos
    # iterate through paragraphs
    for i in range(0, len(paragraphs)):
        text_wrap_overflow = False
        # iterate through words
        for j in range(0, len(paragraphs[i])):
            word = paragraphs[i][j]
            word_surface = font.render(word, antialias, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # reset the x.
                y += line_space_scale * word_height # text wrapping
                if y + word_height > max_height:
                    text_wrap_overflow = True
                    break
            surface.blit(word_surface, (x, y))
            x += word_width + space_width
        x = pos[0]  # reset the x.
        y += paragraph_space_scale * word_height  # new paragraph
        # new paragraph or text wrap overflow
        if y + word_height > max_height or text_wrap_overflow:
            break
    return get_unrendered(paragraphs, p_idx=i, w_idx=j, 
                          return_unrendered=return_unrendered, 
                          is_text_wrap_overflow=text_wrap_overflow)

HEIGHT = 256
WIDTH = 512
def render_wrapper(text, height=HEIGHT, width=WIDTH, fontsize=16, \
    line_space=-1, fixed_width=True, fix_spacing=True, no_partial=False, \
    no_margin=True, white_bg=True):
    array = np.zeros(width*height, dtype=np.int8)
    rendered, rstr = renderer.render(array, text, height, width, \
        fontsize, line_space, fixed_width, fix_spacing, \
        no_partial, no_margin)
    rendered = (255 - rendered.reshape(height, width)) if white_bg else \
        rendered.reshape(height, width)
    return Image.fromarray(rendered, 'L'), rstr

def render_unicode_wrapper(text, height=HEIGHT, width=WIDTH, fontsize=16, \
    line_space=-1, fixed_width=True, fix_spacing=True, no_partial=False, \
    no_margin=True, white_bg=True):
    array = np.zeros(width*height, dtype=np.int8)
    rendered, rstr = renderer.render_unicode(array, text, height, width, \
        fontsize, line_space, fixed_width, fix_spacing, \
        no_partial, no_margin)
    rendered = (255 - rendered.reshape(height, width)) if white_bg else \
        rendered.reshape(height, width)
    return Image.fromarray(rendered, 'L')

def render_text_pangocairo(
        text, 
        width=512, 
        height=256, 
        font_size=5, 
        line_space=0.8, 
        align_tokens=False,
        align_by_space=True,
        tokenizer=None,
        pch_size=16,
        pch_per_tk=4,
        font_family_style="Sans Serif Normal", 
        background_color=(1, 1, 1), 
        text_color=(0, 0, 0)):

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)

    # Paint background color
    context.set_source_rgb(*background_color)
    context.paint()

    # Set text color
    context.set_source_rgb(*text_color)

    # Text layout
    layout = PangoCairo.create_layout(context)
    desc = Pango.font_description_from_string(f'{font_family_style}')
    desc.set_absolute_size(font_size * Pango.SCALE)
    layout.set_font_description(desc)

    if align_tokens:
        # replace spaces with tabs
        if align_by_space:
            text = text.replace(' ', '\t')
        else:
            text = tokenizer.tokenize(text, add_special_tokens=False)
            text = "\t".join(text)

        # calculate max number of tabs that can fit in width
        num_tabs = width // (pch_size * pch_per_tk)
        tab_arr = Pango.TabArray(num_tabs, True)

        # set tab alignment position
        for i in range(num_tabs):
            tab_arr.set_tab(i, Pango.TabAlign.LEFT, pch_size * pch_per_tk * (i + 1))

        # apply tab configs to layout
        layout.set_tabs(tab_arr)

    layout.set_alignment(Pango.Alignment.LEFT)
    layout.set_width(width * Pango.SCALE)
    layout.set_height(height * Pango.SCALE)
    layout.set_text(text, -1)
    layout.set_line_spacing(line_space)

    context.move_to(0, 0) 
    PangoCairo.show_layout(context, layout)
    image_data = surface.get_data()
    pil_image = Image.frombuffer(
        'RGB', (width, height), image_data, 'raw', 'RGBA', 0, 1
    )

    return pil_image

def render_text_pygame(
        text, 
        width=512, 
        height=256,
        display_mode=[512, 256],
        font_size=7,
        line_space_scale=0.6, 
        paragraph_space_scale=0.5, 
        return_unrendered=False,
        font_file="fonts/GoNotoCurrent.ttf",
        antialias=True,
        background_color=pygame.Color('white'),
        text_color=pygame.Color('black'),
        x_pos=0,
        y_pos=0,
        alt_space_width=None,
        color_schema='RGB'):
    '''
    text: string
    width: width of the image
    height: height of the image
    display_mode: display mode of pygame: https://www.pygame.org/docs/ref/display.html#pygame.display.set_mode
    font_size: font size
    line_space_scale: space between lines in the same paragraph
    paragraph_space_scale: space between paragraphs
    return_unrendered: whether to return unrendered text; returns None if set to false or all texts are rendered when set to true
    font_file: font file
    antialias: whether to use antialias (the quality decreases a lot if set to false)
    background_color: background color
    text_color: text color
    x_pos: x position of the text (i.e., distance from the left)
    y_pos: y position of the text (i.e., distance from the top)
    alt_space_width: alternative space width; if set to None, the space width is the same as the width of a space in the font
    color_schema: color schema of the image; 'RGB' or 'RGBA': https://www.pygame.org/docs/ref/image.html#pygame.image.tobytes 
    '''
    
    screen = pygame.display.set_mode(display_mode)
    screen.fill(background_color)
    font = pygame.font.Font(font_file, font_size)
    unrendered_text = blit_text(screen, text, (x_pos, y_pos), font, text_color,
                     return_unrendered, alt_space_width, antialias,
                     line_space_scale, paragraph_space_scale)
    pygame.display.update()
    img = pygame.image.tobytes(screen, color_schema)
    img = Image.frombytes(color_schema, (width, height), img, 'raw')
    return img, unrendered_text

# pangocairo
last_time = time()
for i in range(16):
    render_text_pangocairo(s)
print("Pango cairo: %.2f s" % (time() - last_time))

# in-house
last_time = time()
for i in range(16):
    render_unicode_wrapper(s)
print("In-House: %.2f s" % (time() - last_time))

# pygame
last_time = time()
for i in range(16):
    render_text_pygame(s)
print("PyGame: %.2f s" % (time() - last_time))