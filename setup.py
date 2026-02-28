__version__ = "0.0.1"

import setuptools

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setuptools.setup(
    name="tvgbot",
    version=__version__,
    author="Vasudev Gupta",
    author_email="7vasudevgupta@gmail.com",
    description="virtual clone of @thevasudevgupta",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/thevasudevgupta/tvgbot",
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    install_requires=[
        "tqdm",
        "pydantic",
        "python-dotenv",
        "fire",
        "black",
        "isort",
        "ipdb",
        "anthropic",
        "tweepy",
        "discord.py",
    ],
    classifiers=["Topic :: Scientific/Engineering :: Artificial Intelligence"],
    python_requires=">=3.11",
)
