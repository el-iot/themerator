import argparse
import os.path

from maker import ThemeMaker

PATH = os.path.abspath(__file__).replace("/imagen.py", "")


def main() -> None:

    parser = argparse.ArgumentParser(
        prog="imagen",
        description="Imagen is a tool for building customisable base16 themes from images",
    )

    parser.add_argument(
        "IMAGE_PATH", type=str, help="The path to the image",
    )

    parser.add_argument(
        "THEME_NAME", type=str, help="The name of the theme",
    )

    parser.add_argument(
        "-v",
        "--variant",
        type=int,
        default=None,
        help=(
            "Theme-variant (dark=0, light=1). "
            "If unselected then this will be chosen based "
            "on the available colours in the image"
        ),
    )

    parser.add_argument(
        "-i", "--intensity", type=int, default=100, help="Theme intensity",
    )

    parser.add_argument(
        "-p", "--preview", help="Create a preview the theme", action="store_true"
    )

    args = parser.parse_args()
    variant = {0: "dark", 1: "light"}.get(args.variant)

    maker = ThemeMaker(args.IMAGE_PATH, path=PATH)
    theme = maker.create_theme(
        args.THEME_NAME, variant=variant, intensity=args.intensity
    )

    if args.preview:
        theme.preview()
    else:
        theme.save()
