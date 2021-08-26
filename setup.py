from os import path

from setuptools import find_packages, setup

version = "3.0.0"


# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pytineye",
    version=version,
    description="Python client for the TinEye API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://api.tineye.com/",
    author="TinEye",
    author_email="support@tineye.com",
    license="MIT License",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords=["tineye", "api", "reverse image search"],
    project_urls={
        "Documentation": "https://api.tineye.com/python/docs/",
        "Source": "https://github.com/TinEye/pytineye/",
    },
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    install_requires=[
        "future==0.18.2",
        "urllib3==1.26.6",
        "certifi==2021.5.30",
    ],
    include_package_data=True,
    zip_safe=False,
    tests_require=["nose"],
)
