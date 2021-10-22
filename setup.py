import os
from setuptools import setup, find_packages


PKG_NAME = "clidantic"
LIB_NAME = "clidantic"
VER_FILE = "version.py"


def read_version(package: str, version_file: str) -> str:
    """
    Reads a version string from the given file, returning the corresponding string.
    This is manually read instead of imported because of the setup procedure.
    """
    version_str = "unknown"
    version_path = os.path.join(package, version_file)
    try:
        version_line = open(version_path, "rt").read()
        version_str = version_line.split("=")[-1].rstrip().replace('"', "")
        return version_str
    except EnvironmentError:
        raise RuntimeError(f"Unable to find {version_path} or file is not well formed.")

# read the requirements list
requirements = []
with open("requirements.txt", "r") as file:
    for line in file:
        requirements.append(line)

# read the instructions to be used as long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name=LIB_NAME,
    version=read_version(PKG_NAME, VER_FILE),
    packages=find_packages(exclude=["tests"]),
    license="MIT",
    description="Elengant CLIs merging Click and Pydantic",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6"
)