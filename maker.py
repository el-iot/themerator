from theme import Theme
import colorthief


class ThemeMaker:
    """
    ThemeMaker class
    """

    def __init__(
            self, image: str, path: str
    ):
        """
        Initialise the palette
        """
        self.thief = colorthief.ColorThief(image)
        self.path = path
        self.colours = [self.thief.get_color(1)] + [
            *self.thief.get_palette(color_count=50, quality=1)
        ]

    def create_theme(self, name: str, variant: str = "", intensity: int = 100) -> Theme:
        """
        Create a theme
        """
        return Theme(
            f'base16-{name.lstrip("base16-")}', self.colours, variant, intensity, path=self.path
        )
