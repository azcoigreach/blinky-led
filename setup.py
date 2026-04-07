from setuptools import setup

setup(
    name="blinky",
    version="2.1",
    packages=[
        "blinky",
        "blinky.commands",
        "blinky.media",
        "blinky.media.fonts",
        "blinky.media.images",
    ],
    include_package_data=True,
    install_requires=["click", "Pillow", "requests"],
    entry_points="""
        [console_scripts]
        blinky=blinky.cli:cli
    """,
)
