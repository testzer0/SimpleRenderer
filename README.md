# A Simple Renderer

All available renderers have many bells and whistles, but are slow and/or too sophisticated for easy use for text rendering. This a simple, but fast renderer written in C++ and meshed to Python via [PyBind 11](https://pybind11.readthedocs.io/en/stable/).

We can handle different font sizes, automatic line wrapping, and colors. 

## Usage

Change into the source code directory and build the renderer as follows:
```
cd src/
make
```
This will create a `render.cpython-*` file, which is the python library that imports three functions. The first two are `render` and `render_unicode`. The former can handle only ASCII characters, while the latter can work with Unicode but is around `3.5%` slower. The signature for both python functions is

```
def render_either(text: string, height: int, width: int, fontsize: int,
    line_space: int, fixed_width: bool, fix_spacing: bool, no_partial: bool,    no_margin: bool, white_bg: bool)
```
Above, `text`, `height`, `width` and `fontsize` are self-explanatory. If `line_space` is not set, a default of `(fontsize+1)//2` pt is used. If `fixed_width` is set, the first copy of a character is used for all occurences. In practice, this does not seem to cause any noticable drop in quality and is recomended. We also recommend `fix_spacing` that avoids weird non-uniform spaces in the text. If `no_partial` is set, rendering stops at the point where the next line would be partially cut off due to exceeding the confines. Otherwise, rendering continues until the upper-left corner of the character glyph goes out-of-vertical-bounds. The option `no_margin` is self-explanatory. Finally, `white_bg` creates a white background with black text (otherwise, the opposite happens). The two functions return the rendered text as a linearized numpy array and the rendered portion of the string. The third function, `only_render_unicode` has the same signature but returns the rendered array and is slightly faster.

To see a test run, type
```
python3 src/test.py
```
and then look under `outputs/different-sizes/` for the rendered images. If `-v / --verbose` is set, the rendered portions of the text are printed.

## Files
In `src/`, the files `render.h` and `render.cpp` implement the rendering code. The file `main.cpp` rounds off the C++ portion to be able to be executable when compiled. The file `renderer.cpp` defines the `pybind11` bindings while `Makefile` defines rules to compile the project. The `benchmark-*.py` files are some simple benchmarks, and `test.py` shows an example of the renderer's usage from Python. Finally, `fonts/` store the `.ttf` files of the used fonts and `outputs/` is where the outputs go.