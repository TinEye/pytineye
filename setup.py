from setuptools import setup, find_packages


version = "2.0.1"

setup(
    name="pytineye",
    version=version,
    description="Python client for the TinEye API.",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
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
        "pycryptodome==3.10.1",
        "urllib3[secure]==1.26.4",
    ],
)
