from setuptools import setup, find_packages

version = '1.3'

setup(
    name='pytineye',
    version=version,
    description="Python client for the TinEye Commercial API.",
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'],
    keywords=['tineye', 'reverse image search'],
    author='TinEye',
    author_email='support@tineye.com',
    url='https://api.tineye.com/',
    license='MIT License',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    tests_require=[
        'nose'],
    install_requires=[
        'future==0.16',
        'pycryptodome==3.6.6',
        'urllib3[secure]==1.22'
    ]
)
