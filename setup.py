from setuptools import setup, find_packages


version = "3.0.0"

setup(
    name="pytineye",
    version=version,
    description="Python client for the TinEye API.",
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
    author="TinEye",
    author_email="support@tineye.com",
    url="https://api.tineye.com/",
    license="MIT License",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    zip_safe=False,
    tests_require=["nose"],
    install_requires=[
        "future==0.18.2",
        "urllib3==1.26.6",
        "certifi==2021.5.30",
    ],
)
