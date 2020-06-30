```
                                              _                    _  __
                                             | |__   __ _ ___  ___/ |/ /_
                                             | '_ \ / _` / __|/ _ \ | '_ \
                                             | |_) | (_| \__ \  __/ | (_) |
                                             |_.__/ \__,_|___/\___|_|\___/
    gg
    ""
    gg    ,ggg,,ggg,,ggg,     ,gggg,gg    ,gggg,gg   ,ggg,    ,ggg,,ggg,
    88   ,8" "8P" "8P" "8,   dP"  "Y8I   dP"  "Y8I  i8" "8i  ,8" "8P" "8,
    88   I8   8I   8I   8I  i8'    ,8I  i8'    ,8I  I8, ,8I  I8   8I   8I
  _,88,_,dP   8I   8I   Yb,,d8,   ,d8b,,d8,   ,d8I  `YbadP' ,dP   8I   Yb,
  8P""Y88P'   8I   8I   `Y8P"Y8888P"`Y8P"Y8888P"888888P"Y8888P'   8I   `Y8
                                             ,d8I'
                                           ,dP'8I
                                          ,8"  8I
                                          I8   8I
                                          `8, ,8I
                                           `Y8P"
```

<h1>base16-imagen</h1>
A python script that generates base16 themes based on given images.
Currently only generates base16 themes for <a href='https://github.com/chriskempson/base16-shell'>shell</a> and <a href='https://github.com/chriskempson/base16-vim'>vim</a> (but creating more should be easy enough). <br>

Generates .vim and .sh files and optionally saves them to configurable destinations.

<h2>Why?</h2>
I personally love <a href='https://github.com/chriskempson/base16'>base16</a>: I am always working at a terminal and being able to change my theme quickly and easily is a great way to stay engaged. With that being said, sometimes I find myself modifying themes manually in the interest of creating new and interesting ones. This gets a bit tricky once you start needing to synchronise changes made to base16-vim and base16-shell files. The purpose of this project is to generate themes from your favourite images that are (hopefully) very palettable and make reading text at terminal easy and engaging.

<h2>Usage</h2>
Currently this package only runs inside a python (>3) environment. If there is sufficient interest it could be expanded to run as a shell-script.

```python
>>> from base16_imagen import ThemeMaker
>>> maker = ThemeMaker({some path to an image})
>>> theme = maker.create_theme('my-theme', variant='dark')
    {theme will render}
>>> theme.save() # not providing paths will save the themes to your current directory
>>> exit()
```

```zsh
$ ls
  my-theme.sh
  my-theme.vim
$ mv my-theme.sh ~/.config/base16-shell/scripts/              # this is where my shell themes are
$ mv my-theme.vim  ~/.config/nvim/plugged/base16-vim/colors/  # this is where my vim themes are
$ source ~/.zshrc                                             # or start a new terminal session
$ my-theme
{viola!}
```

<h2>Examples</h2>
Here are some of my favourite images and the corresponding themes they generate <br>

TODO: add examples

<h2> Relevant Projects </h2>

<list>
    <a href="https://github.com/chriskempson/base16">Base16</a><br>
    <a href="https://github.com/fengsp/color-thief-py">Color-Thief-Python</a>
</list>
