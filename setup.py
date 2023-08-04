from pathlib import Path

from setuptools import setup, find_packages


def read(filename):
    return Path(filename).read_text()


setup(
    name="jiji",
    version="0.0.4",
    packages=find_packages(),
    url="https://github.com/wizkiye/pyJiji",
    license="",
    author="Kidus",
    author_email="",
    description="",
    requires=["httpx"],
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
)
