<h1> Themerator </h1>
A Base16 Theme-Generator for Shell and Vim <br>
Generates .vim and .sh files and saves them to configurable destinations.

This is not very functional right now and a work-in-progress. Can only currently be used in a python environment (Python > 3.6).

<h1> Usage </h1>

![demo](/assets/demo.gif)

```
$ ipython
>>> from themerator import Theme
>>> theme = theme({path to image})
>>> theme.render() # previews the theme
>>> theme.save(theme name)
>>> exit()
$ source ~/.zshrc
$ base16_{theme name}
```

<h1> Examples </h1>
<h2> Before </h2>

Here is how your terminal might look *before* the magic happens

![Before](/assets/before.png)

<h2> After </h2>

Here are some example images and their corresponding themes

<p align="center">
    <img src="assets/walt.jpg" width="320" height="320"/> <img src="assets/walt_theme.png" width="480" height="320"/><br>
    <img src="assets/poppies.jpeg" width="320" height="320"/> <img src="assets/poppies_theme.png" width="480" height="320"/><br>
    <img src="assets/matrix.jpg" width="320" height="320"/> <img src="assets/matrix_theme.png" width="480" height="320"/><br>
    <img src="assets/flower.jpg" width="320" height="320"/> <img src="assets/flower_theme.png" width="480" height="320"/><br>
</p>

<h1> Relevant Projects </h1>

<list>
    <a href="https://github.com/chriskempson/base16">Base16</a> <br>
    <a href="https://github.com/fengsp/color-thief-py">Color-Thief-Python</a>
</list>
