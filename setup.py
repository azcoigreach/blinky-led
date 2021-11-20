from setuptools import setup

setup(
    name="blinky",
    version="0.1",
    packages=["BlinkyLED", "BlinkyLED.commands"],
    include_package_data=True,
    install_requires=["click"],
    entry_points="""
        [console_scripts]
        blinky=BlinkyLED.cli:cli
    """,
)
