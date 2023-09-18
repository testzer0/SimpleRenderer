import numpy as np
import os
import renderer
from PIL import Image
from time import time

import shutil
from multiprocessing import Pool, Process
import random
import string
import numpy as np

HEIGHT = 256
WIDTH = 512

def random_word(min_length=3, max_length=10, full_punctuation=True):
    punctuation = string.punctuation if full_punctuation else \
        '.?$@!%^&*()'
    wlength = random.randint(min_length, max_length)
    return ''.join(random.choice(string.ascii_letters + \
        string.digits + punctuation) for x in range(wlength))
    
def random_doc(n_words=200, min_length=3, max_length=10):
    return " ".join([random_word(min_length, max_length) for _ \
        in range(n_words)])
    
def generate_data(n_examples=500, n_min_words=100, n_max_words=300, \
    min_length=3, max_length=10):
    return [random_doc(n_words=random.randint(n_min_words, n_max_words), \
        min_length=min_length, max_length=max_length) for _ in range(n_examples)]    
    
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

def render_inhouse(text):
    return render_wrapper(text)[0]

def render_inhouse_unicode(text):
    return render_unicode_wrapper(text)[0]

def run_test(test_dir, n_examples=500, n_min_words=100, n_max_words=300, \
    min_length=3, max_length=10, save=False, n_procs=16):    
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir, ignore_errors=True)
    os.makedirs(test_dir, exist_ok=True)
    
    data = generate_data(n_examples=n_examples, n_min_words=n_min_words, \
        n_max_words=n_max_words, min_length=min_length, max_length=max_length)
    copy1 = []

    print("{} examples, {}-{} words of {}-{} characters each".format(\
        n_examples, n_min_words, n_max_words, min_length, max_length))
    print("{} parallel processes".format(n_procs))
    
    print("** Sequential **")
    start1 = time()
    for i in range(len(data)):
        copy1.append(render_inhouse_unicode(data[i]))
    end1 = time()
    print("Time = {:.3f} seconds\n".format(end1-start1))
    
    print("** Parallel **")
    start2 = time()
    with Pool(n_procs) as p:
        copy2 = p.map(render_inhouse_unicode, data)
    end2 = time()
    print("Time = {:.3f} seconds\n".format(end2-start2))
    
    speedup = (end1-start1)/(end2-start2)
    pcent = 100.0*speedup/n_procs
    print("Speedup = {:.2f}x ({:.2f}% of ideal)".format(speedup, pcent))
    
    n = min(5, len(data))
    print("Saving {} random examples...".format(n))
    
    indices = np.random.permutation(len(data))[:n].tolist()
    for i, idx in enumerate(indices):
        out_text = os.path.join(test_dir, "{}.txt".format(i+1))
        with open(out_text, "w+") as f:
            f.write(data[i])
        out_png = os.path.join(test_dir, "{}.png".format(i+1))
        copy2[i].save(out_png)   
        
    print("Done")
    
if __name__ == '__main__':
    run_test(test_dir="outputs/multithreading-samples")