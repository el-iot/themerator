"""
Themerator
A Base16 Theme-Generator for Shell and Vim
"""
import math
import os
from typing import Union

import colorthief
import structlog


class Theme:
    """
    Theme Class
    """

    def __init__(
        self, image_path: str, dark: bool = True, darkness_boundaries: Union[list, None] = None,
    ):
        """
        Initialise the palette
        """
        self.logger = structlog.get_logger(name="themerator")
        self.thief = colorthief.ColorThief(image_path)
        self.dark = dark
        self.palette = self.get_palette(darkness_boundaries)
        self.designations = self.assign_palette()
        self.render()

    @staticmethod
    def _rgb_to_hex(red, green, blue, separator="") -> str:
        """
        Convert an RGB-defined colour to a hex-defined colour with a given separator
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

            text = str(colour)

        text = "█████" + text

        if isinstance(colour, tuple):
            colour = self._rgb_to_hex(*colour).upper()

        hexint = int(colour, 16)
        print(f"\x1B[38;2;{hexint>>16};{hexint>>8&0xFF};{hexint&0xFF}m{text}\x1B[0m")

    def filter_palette(self, colours: list, max_retries=50) -> list:
        """
        Filter a palette down so it has atleast 16 colours that are as distinct as possible
        """

        colours = sorted(colours, key=lambda x: sum(x) * (1 if self.dark else -1))
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

        if n < 8:
            raise ValueError(f"can only find {n} (< 8) distinct colours")

        self.logger.warning(f"only found distinct {n} colours")
        return candidates

    def get_similarity(self, c1, c2) -> float:
        """
        Get the similarity between colours
        """
        return 1 - math.sqrt(sum([(a - b) ** 2 for a, b in zip(c1, c2)])) / math.sqrt(
            sum([255 ** 2 for _ in range(3)])
        )

    def filter_by_similarity(self, colours, similarity_threshold) -> list:
        """
        Filter colours down by similarity
        """
        if not colours:
            return []

        colours = colours.copy()
        background = colours.pop(0)
        chosen = [background]

        background_similarity_threshold = max(
            1 - (1 - similarity_threshold) * 2, similarity_threshold
        )

        for colour in colours:

            if (
                chosen
                and any(
                    self.get_similarity(colour, choice) > similarity_threshold for choice in chosen
                )
                or (255 - abs(sum(colour) - sum(background)) / 3) / 255
                > background_similarity_threshold
            ):
                continue

            chosen.append(colour)

        return chosen

    def assign_palette(self) -> dict:
        """
        Designate up to 16 colours in a palette to a Base16 colour number
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

        order = {
            "dark": [
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
            ],
            "light": [
                ("color00", "light"),  # background
                ("color07", "dark"),  # foreground
                ("color01", "red"),  # red
                ("color02", "green"),  # green
                ("color04", "blue"),  # blue
                ("color03", "yellow"),  # yellow
                ("color05", "magenta"),  # magenta
                ("color06", "cyan"),  # cyan
                ("color18", "light"),  # ?
                ("color19", "light"),  # ?
                ("color20", "light"),  # ?
                ("color21", "light"),  # ?
                ("color15", "light"),  # ?
                ("color16", "light"),  # ?
                ("color17", "light"),  # ?
                ("color08", "light"),  # ?
            ],
        }

        reuse_palette = {
            "color08": (
                ["color01", "color02", "color03", "color04", "color05", "color06"],
                "dark",
            ),
            "color18": (
                ["color01", "color02", "color03", "color04", "color05", "color06"],
                "light",
            ),
            "color19": ["color04"],
            "color20": ["color07"],
            "color21": ["color00"],
            "color15": ["color01"],
            "color16": ["color06"],
            "color17": ["color02"],
        }

        designations = {}

        tone = "dark" if self.dark else "light"

        def get_preference(options, metric_name=None):

            if metric_name is None:
                return designations[options]

            return sorted([designations[option] for option in options], key=metrics[metric_name])[0]

        for label, metric_name in order[tone]:

            palette = sorted(palette, key=metrics[metric_name])
            if palette:
                designations[label] = palette.pop()
            else:
                designations[label] = get_preference(*reuse_palette[label])

        return designations

    def prominence(self, rgb, highlights) -> int:
        """
        Score a colour based on the prominence of highlights
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

    def get_palette(self, darkness_boundaries) -> list:
        """
        Get a palette from a path to an image
        """
        if darkness_boundaries is None:

            if self.dark:
                darkness_boundaries = [25, None]
            else:
                darkness_boundaries = [None, 225]

        [lower_bound, upper_bound] = darkness_boundaries

        colours = [
            colour
            for colour in self.thief.get_palette(color_count=50, quality=1)
            if (
                (lower_bound is None or sum(colour) / 3 > lower_bound)
                and (upper_bound is None or sum(colour) / 3 < upper_bound)
            )
        ]

        palette = self.filter_palette(colours)

        return palette

    def render(self, sort=lambda x: sum(x)) -> None:
        """
        Render every colour in palette
        """
        for name, colour in self.designations.items():
            self._render(colour, text=f"{colour} -> {name}")

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

        if not (vim or shell):
            raise ValueError("Must select at least one or 'shell' or 'vim'")

        if vim:
            with open("assets/theme_templates/vim.txt", "r") as file:
                vim = file.read()
            vim = vim.replace("__theme_name__", theme_name)

        if shell:
            with open("assets/theme_templates/shell.txt", "r") as file:
                shell = file.read()
            shell = shell.replace("__theme__name__", theme_name)

        for label, code in self.designations.items():

            hexcode = self._rgb_to_hex(*code, separator="/")

            if shell:
                shell = shell.replace(f"__{label}__", hexcode)

            if vim:
                vim_hexcode = hexcode.replace("/", "")
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
