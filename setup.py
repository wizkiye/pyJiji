from pathlib import Path

from setuptools import setup, find_packages


def read(filename):
    return Path(filename).read_text()


setup(
    name="jiji",
    version="",
    packages=find_packages(),
    url="",
    license="",
    author="Kidus",
    author_email="",
    description="",
    requires=["httpx"],
)
