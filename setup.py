from pathlib import Path

from setuptools import setup, find_packages


def read(filename):
    return Path(filename).read_text()


setup(
    name="jiji",
    version="0.1.0",
    packages=find_packages(),
    url="https://github.com/wizkiye/pyJiji",
    license="",
    author="Kidus",
    author_email="",
    description="Unofficial async API client and CLI for Jiji Ethiopia (jiji.com.et)",
    install_requires=["httpx>=0.24.1"],
    entry_points={"console_scripts": ["jiji=jiji.cli:main"]},
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
)
