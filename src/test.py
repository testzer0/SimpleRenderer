import numpy as np
import PIL
import os
import sys
import renderer
import matplotlib.pyplot as plt
from PIL import Image

WIDTH = 512
HEIGHT = 256

teststring = open("../../screenshotlm/tmp/text512256br").read()

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
    return Image.fromarray(rendered, 'L'), rstr

def main():
    fontsizes = [5, 7, 9, 11, 13, 15]
    if len(sys.argv) > 1 and sys.argv[1] in ['--verbose', '-v']:
        verbose = True
    elif len(sys.argv) > 1:
        print("Usage: python3 test.py [-v / --verbose]")
    else:
        verbose = False
    for fontsize in fontsizes:
        image, rstr = render_unicode_wrapper(teststring, fontsize=fontsize, \
            fix_spacing=True, no_partial=True, no_margin=False)
        image.save("outputs/different-sizes/test-{}.png".format(fontsize))
        if verbose:
            print("Font size {} - last 10 words:".format(fontsize))
            print(" ".join(rstr.strip().split()[-10:]))
    
if __name__ == '__main__':
    main()
