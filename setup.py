from setuptools import setup

setup(
    name="blinky",
    version="2.1",
    packages=["blinky", "blinky.commands"],
    include_package_data=True,
    install_requires=["click"],
    entry_points="""
        [console_scripts]
        blinky=blinky.cli:cli
    """,
)
