__version__ = "0.0.1"

import setuptools

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

setuptools.setup(
    name="safeclaw",
    version=__version__,
    author="Vasudev Gupta",
    author_email="7vasudevgupta@gmail.com",
    description="can we make openclaw safe? developed by @thevasudevgupta",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/thevasudevgupta/safeclaw",
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    install_requires=[
        "tqdm",
        "pydantic",
    ],
    classifiers=["Topic :: Scientific/Engineering :: Artificial Intelligence"],
    python_requires=">=3.11",
)
