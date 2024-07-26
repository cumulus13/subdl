import io
from setuptools import setup, find_packages
import shutil
import os

NAME = "subdl"

shutil.copy2('__version__.py', NAME)

# Read the README file
with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

# Read the version from idm/__version__.py
#version = {}
#with open(os.path.join(NAME, "__version__.py")) as fp:
    #exec(fp.read(), version)
#version = version['version']

# Determine the packages based on the extra provided
#extra_packages = [NAME]

import __version__

setup(
    name=NAME,
    version=__version__.version,
    url="https://github.com/cumulus13/subdl",
    project_urls={
        "Documentation": "https://github.com/cumulus13/subdl",
        "Code": "https://github.com/cumulus13/subdl",
    },
    license="GPL",
    author="cumulus13",
    author_email="cumulus13@gmail.com",
    maintainer="cumulus13 Team",
    maintainer_email="cumulus13@gmail.com",
    description="SubDL.com Downloader",
    long_description=readme,
    long_description_content_type="text/markdown",
    package_data={'subdl': ['*.ini']}, 
    packages=find_packages(),
    install_requires=[
        'argparse',
        'rich', 
        'configset', 
        'pydebugger',
        'make_colors', 
        'requests'
    ],
    entry_points={
        "console_scripts": [
            #"subdl = subdl.__main__:main",
            "subdl = subdl.Subdl:usage",
        ]
    },
    data_files=['__version__.py', 'README.md'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Update if your license is different
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
    ],
    python_requires='>=3.6',
)
