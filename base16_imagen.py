import math
import os
from typing import Callable, Dict, List, Tuple, Union

import colorthief
import structlog


class Theme:
    """
    Theme class
    """

    def __init__(self, name: str, colours: List, variant: str, intensity: int) -> None:
        """
        Initialise a theme
        """
        self.name = name
        self.generate_designations(colours, variant, intensity)
        self.logger = structlog.getLogger(f"{self.name}-theme")
        self.render()

    def _render(self, colour: Union[tuple, str], text: str = None) -> None:
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

    def render(self, sort: Callable = lambda x: sum(x)) -> None:
        """
        Render every colour in palette
        """
        if self.designations is None:
            raise ValueError("must designate first")

        for name, colour in self.designations.items():
            self._render(colour, text=f"{colour} -> {name}")

    def assign_palette(self) -> Dict:
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

        designations: Dict = {}

        tone = "dark" if self.dark else "light"

        def get_preference(options: List, metric_name: str = "") -> tuple:
            """
            Get reuse preferences
            """
            if metric_name == "":
                return designations[options]

            return sorted(
                [designations[option] for option in options], key=metrics[metric_name]
            )[0]

        for label, metric_name in order[tone]:

            palette = sorted(palette, key=metrics[metric_name])
            if palette:
                designations[label] = palette.pop()
            else:
                designations[label] = get_preference(*reuse_palette[label])

        return designations

    def prominence(self, rgb: Tuple, highlights: List) -> int:
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

    @staticmethod
    def _rgb_to_hex(red: int, green: int, blue: int, separator: str = "") -> str:
        """
        Convert an RGB-defined colour to a hex-defined colour with a given separator
        """

        _pad = lambda x: "0" * (2 - len(x)) + x

        return separator.join(_pad(hex(colour)[2:]) for colour in [red, green, blue])

    def generate_designations(
        self, colours: List, variant: str, intensity: int
    ) -> None:
        """
        Generate the theme designations
        """
        self.palette = self.generate_palette(colours, variant, intensity)
        self.designations = self.assign_palette()

    def save(
        self,
        vim: bool = True,
        shell: bool = True,
        vim_path: str = ".",
        shell_path: str = ".",
    ) -> None:
        """
        Save theme to a .vim file and a .sh file

        Parameters
        ----------
        vim: whether or not to produce a vim-file
        shell: whether or not to produce a shell-file
        vim_path : where the vim-theme will be saved (Default value is current directory)
        shell_path : where the shell-theme will be saved (Default value is current directory)
        """

        if not self.designations:
            raise ValueError("No colours designated")

        if not (vim or shell):
            raise ValueError("Must select at least one or 'shell' or 'vim'")

        if vim:
            self._save_vim(vim_path)

        if shell:
            self._save_shell(shell_path)

    def _save_vim(self, path: str) -> None:
        """
        Save base16 vim theme
        """

        with open("assets/theme_templates/vim.txt", "r") as file:
            vim_file = file.read()
        vim_file = vim_file.replace("__theme_name__", self.name)

        for label, code in self.designations.items():

            hexcode = self._rgb_to_hex(*code, separator="/").replace("/", "")
            vim_file = vim_file.replace(f"__{label}__", hexcode).replace(
                f"__hashed_{label}__", f"#{hexcode}"
            )

        with open(
            f"{os.path.expanduser(path)}/colors/base16-{self.name}.vim", "w",
        ) as file:
            file.write(vim_file)

    def _save_shell(self, path: str) -> None:
        """
        Save base16 shell theme
        """
        with open("assets/theme_templates/shell.txt", "r") as file:
            shell_file = file.read()

        shell_file = shell_file.replace("__theme__name__", self.name)

        for label, code in self.designations.items():

            hexcode = self._rgb_to_hex(*code, separator="/")
            shell_file = shell_file.replace(f"__{label}__", hexcode)

        with open(
            f"{os.path.expanduser(path)}/scripts/base16-{self.name}.sh", "w"
        ) as file:
            file.write(shell_file)

    def generate_palette(self, colours: List, variant: str, intensity: int) -> list:
        """
        Get the palette of an image
        """
        dominant_colour = colours.pop(0)

        if not variant:

            background = sum(dominant_colour) / 3
            dark = background < (255 / 2)

            if dark:
                darkness_boundaries = [background, 255 * (intensity / 100)]
            else:
                darkness_boundaries = [255 * (1 - intensity / 100), background]

        elif variant == "dark":
            darkness_boundaries = [255 * (1 - intensity / 100), 255]

        else:
            darkness_boundaries = [0, 255 * (intensity / 100)]

        self.dark = variant == "dark" or (variant is None and dark)

        [lower_bound, upper_bound] = darkness_boundaries

        colours = [
            colour
            for colour in [dominant_colour] + colours
            if (sum(colour) / 3 >= lower_bound and sum(colour) / 3 <= upper_bound)
        ]

        palette = self.filter_palette(colours)

        return palette

    def filter_palette(self, colours: list, max_retries: int = 50) -> list:
        """
        Filter a palette down so it has atleast 16 colours that are as distinct as possible
        """
        colours = sorted(colours, key=lambda x: sum(x) * (1 if self.dark else -1))
        left, right = 0.0, 1.0

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

        if n < 16:
            self.logger.warning(f"only found distinct {n} colours")

        return candidates

    def get_similarity(self, c1: List[int], c2: List[int]) -> float:
        """
        Get the similarity between colours
        """
        return 1 - math.sqrt(sum([(a - b) ** 2 for a, b in zip(c1, c2)])) / math.sqrt(
            sum([255 ** 2 for _ in range(3)])
        )

    def filter_by_similarity(self, colours: List, similarity_threshold: float) -> List:
        """
        Filter colours down by similarity
        """
        if not colours:
            return []

        colours = colours.copy()
        background = colours.pop(0)
        chosen = [background]

        background_similarity_threshold = similarity_threshold ** 4

        for colour in colours:

            if (
                chosen
                and any(
                    self.get_similarity(colour, choice) > similarity_threshold
                    for choice in chosen
                )
                or (255 - abs(sum(colour) - sum(background)) / 3) / 255
                > background_similarity_threshold
            ):
                continue

            chosen.append(colour)

        return chosen


class ThemeMaker:
    """
    ThemeMaker class
    """

    def __init__(
        self, image_path: str,
    ):
        """
        Initialise the palette
        """
        self.logger = structlog.get_logger(name="theme-maker")
        self.thief = colorthief.ColorThief(image_path)

        self.logger.info(f"Getting colours from image ({image_path})")

        self.colours = [self.thief.get_color(1)] + [
            *self.thief.get_palette(color_count=50, quality=1)
        ]

    def create_theme(self, name: str, variant: str = "", intensity: int = 100) -> Theme:
        """
        Create a theme
        """
        return Theme(name, self.colours, variant, intensity)
