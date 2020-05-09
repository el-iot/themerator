"""
Sweet16
A Base16 Theme-Generator for Shell and Vim
"""
import math
import os
from typing import Union

import colorthief


class ThemeMaker:
    """
    ThemeMaker Class
    """

    def __init__(self, image_path: str, darkness_threshold=0, dominant_background=False):
        """
        Initialise the palette

        Parameters
        ----------
        image_path : the path to the image

        darkness_threshold: the minimum darkness of any colour chosen from the image.
        'Darkness' is defined as the average of the red, green and blue components of the colour.

        dominant_background (experimental): whether or not to use the dominant colour from the image
        as the background colour of the theme
            (Default value = "")

        """
        self.thief = colorthief.ColorThief(image_path)
        self.palette = self.get_palette(dominant_background, darkness_threshold)
        self.designations = self.assign_palette()

    @staticmethod
    def _rgb_to_hex(red, green, blue, separator="") -> str:
        """
        Convert an RGB-defined colour to a hex-defined colour with a given separator

        Parameters
        ----------
        red : the red-value in the colour; [0, 256)
        green : the green-value in the colour; [0, 256)
        blue : the blue-value in the colour; [0, 256)
        separator : the separator for each hex-component
            (Default value = "")

        Returns
        -------
        The hexcode for the colour
        """
        for colour in [red, green, blue]:
            assert isinstance(colour, (int, float)) and 0 <= colour < 256

        _pad = lambda x: "0" * (2 - len(x)) + x

        return separator.join(_pad(hex(colour)[2:]) for colour in [red, green, blue])

    def _render(self, colour: Union[tuple, str], text=None) -> None:
        """
        Render helper
        """
        if text is None:
            text = f"█████ {colour}"

        if isinstance(colour, tuple):
            colour = self._rgb_to_hex(*colour).upper()

        hexint = int(colour, 16)
        print(f"\x1B[38;2;{hexint>>16};{hexint>>8&0xFF};{hexint&0xFF}m{text}\x1B[0m")

    def filter_palette(self, colours: list, dominant_background: bool, max_retries=50) -> list:
        """
        Filter a palette down so it has atleast 16 colours that are as distinct as possible

        Parameters
        ----------
        colours : a list of colours
        dominant_background : whether or not to use the dominant colour from the image as the background colour for the theme
        max_retries : the number of binary-search iterations to perform before concluding that no distinct colours can be found.
            (Default value = 50)

        Returns
        -------
        A list of chosen colours
        """

        colours = sorted(colours, key=lambda x: sum(x))
        left, right = 0, 1

        for _ in range(max_retries):

            middle = (left + right) / 2
            candidates = self.filter_by_similarity(colours, middle)
            n = len(candidates)

            if n < 16:
                left = middle
            elif n > 16:
                right = middle
            else:
                return candidates

        raise RecursionError(f"cannot find sufficiently dissimilar colours; cannot filter")

    def get_similarity(self, c1, c2) -> float:
        """
        Get the similarity between colours

        Parameters
        ----------
        c1 : the first RGB-colour
        c2 : the second RGB-colour

        Returns
        -------
        The percentage similarity between the two colours
        """
        return 1 - math.sqrt(sum([(a - b) ** 2 for a, b in zip(c1, c2)])) / math.sqrt(
            sum([255 ** 2 for _ in range(3)])
        )

    def filter_by_similarity(self, colours, similarity_threshold) -> list:
        """
        Filter colours down by similarity

        Parameters
        ----------
        colours : the list of colours to be filtered
        similarity_threshold : the maximum-allowable-similarity between any two colours

        Returns
        -------
        A filtered list of colours
        """
        chosen = [self.dominant_colour] if hasattr(self, "dominant_colour") else []

        for colour in colours:
            if chosen and any(
                self.get_similarity(colour, choice) > similarity_threshold for choice in chosen
            ):
                continue
            chosen.append(colour)

        return chosen

    def assign_palette(self) -> dict:
        """
        Designate 16 colours in a palette to a Base16 colour number
        """

        palette = self.palette.copy()

        metrics = {
            "dark": lambda colour: -sum(colour),
            "light": lambda colour: sum(colour),
            "red": lambda colour: self.prominence(colour, ["red"]),
            "green": lambda colour: self.prominence(colour, ["green"]),
            "blue": lambda colour: self.prominence(colour, ["blue"]),
            "cyan": lambda colour: self.prominence(colour, ["green", "blue"]),
            "magenta": lambda colour: self.prominence(colour, ["red", "blue"]),
            "yellow": lambda colour: self.prominence(colour, ["red", "green"]),
        }

        order = [
            ("color00", "dark"),  # background
            ("color07", "light"),  # foreground
            ("color01", "red"),  # red
            ("color02", "green"),  # green
            ("color04", "blue"),  # blue
            ("color03", "yellow"),  # yellow
            ("color05", "magenta"),  # magenta
            ("color06", "cyan"),  # cyan
            ("color18", "dark"),  # ?
            ("color19", "dark"),  # ?
            ("color20", "dark"),  # ?
            ("color21", "dark"),  # ?
            ("color15", "dark"),  # ?
            ("color16", "dark"),  # ?
            ("color17", "dark"),  # ?
            ("color08", "dark"),  # ?
        ]

        designations = {}

        for label, metric_name in order:

            if label == "color00" and hasattr(self, "dominant_colour"):
                designations[label] = self.dominant_colour
            else:
                palette = sorted(palette, key=metrics[metric_name])
                designations[label] = palette.pop()

        return designations

    def prominence(self, rgb, highlights) -> int:
        """
        Score a colour based on the prominence of highlights

        Parameters
        ----------
        rgb : tuple: the chosen colour
        highlights : list : which primary colours are desired

        Returns
        -------
        An integer
        """
        if not isinstance(highlights, list):
            highlights = [highlights]

        if any(highlight not in ["red", "green", "blue"] for highlight in highlights):
            raise ValueError("Bad highlight selection")

        desired, undesired = [], []
        for colour, string in zip(rgb, ["red", "green", "blue"]):
            if string in highlights:
                desired.append(colour)
            else:
                undesired.append(colour)

        return min([d - u for d in desired for u in undesired])

    def get_palette(self, dominant_background, darkness_threshold) -> list:
        """
        Get a palette from a path to an image

        Parameters
        ----------
        dominant_background : Whether or not to use the dominant colour from the image as the background colour
        darkness_threshold: the minimum darkness of any colour chosen from the image.
        'Darkness' is defined as the average of the red, green and blue components of the colour.

        Returns
        -------
        A filtered list of colours
        """
        colours = [
            colour
            for colour in self.thief.get_palette(color_count=50, quality=1)
            if sum(colour) / 3 > darkness_threshold
        ]

        palette = self.filter_palette(colours, dominant_background)

        return palette

    def render(self, sort=lambda x: sum(x)) -> None:
        """
        Render every colour in palette

        Parameters
        ----------
        sort : the metric by which to sort the colours
            (Default value = lambda x: sum(x))
        """
        for colour in sorted(self.palette, key=sort):
            self._render(colour)

    def save(
        self,
        theme_name,
        vim=True,
        shell=True,
        base16_vim_path="~/.config/nvim/plugged/base16-vim",
        base16_shell_path="~/.config/base16-shell",
    ) -> None:
        """
        Save theme to a .vim file and a .sh file

        Parameters
        ----------
        theme_name : the name of your theme
        vim: whether or not to produce a vim-file
        shell: whether or not to produce a shell-file
        base16_vim_path : the path to your base16-vim directory
            (Default value = "~/.config/nvim/plugged/base16-vim")
        base16_shell_path : the path to your base16-shell directory
            (Default value = "~/.config/base16-shell")
        """

        if not self.designations:
            raise ValueError("No colours designated")

        if not vim or shell:
            raise ValueError("Must select at least one or 'shell' or 'vim'")

        if vim:
            with open("templates/vim.txt", "r") as file:
                vim = file.read()
            vim = vim.replace("__theme_name__", theme_name)

        if shell:
            with open("templates/shell.txt", "r") as file:
                shell = file.read()
            shell = shell.replace("__theme__name__", theme_name)

        for label, code in self.designations.items():

            shell_hexcode = self._rgb_to_hex(*code, separator="/")
            if shell:
                shell = shell.replace(f"__{label}__", shell_hexcode)

            if vim:
                vim_hexcode = shell_hexcode.replace("/", "")
                vim = vim.replace(f"__{label}__", vim_hexcode)
                vim = vim.replace(f"__hashed_{label}__", f"#{vim_hexcode}")

        if vim:
            base16_vim_path = os.path.expanduser(base16_vim_path)
            with open(f"{base16_vim_path}/colors/base16-{theme_name}.vim", "w",) as file:
                file.write(vim)

        if shell:
            base16_shell_path = os.path.expanduser(base16_shell_path)
            with open(f"{base16_shell_path}/scripts/base16-{theme_name}.sh", "w") as file:
                file.write(shell)
