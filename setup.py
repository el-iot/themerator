from setuptools import setup, find_packages

setup(
    name="imagen",
    version="1.0",
    entry_points={"console_scripts": ["imagen = imagen:main"]},
    packages=find_packages(),
)
