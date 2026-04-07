from setuptools import find_packages, setup

setup(
    name="blinky",
    version="3.0.0",
    packages=find_packages(include=["app", "app.*"]),
    include_package_data=True,
    package_data={
        "app": [
            "web/templates/*.html",
            "web/static/*.css",
            "media/fonts/*",
            "media/images/*",
        ]
    },
    python_requires=">=3.13",
    install_requires=[
        "click>=8.1",
        "fastapi>=0.116",
        "httpx>=0.28",
        "Jinja2>=3.1",
        "Pillow>=11.0",
        "pydantic>=2.10",
        "python-dotenv>=1.0",
        "PyYAML>=6.0",
        "psutil>=6.1",
        "uvicorn>=0.34",
    ],
    extras_require={
        "dev": ["pytest>=8.3", "pytest-asyncio>=0.25"],
        "pi5": ["adafruit-blinka-raspberry-pi5-piomatter>=1.0.0"],
    },
    entry_points="""
        [console_scripts]
        blinky=app.cli:cli
    """,
)
