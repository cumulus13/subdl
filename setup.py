import io
from setuptools import setup, find_packages
import shutil
import os

NAME = "subdl"

#shutil.copy2('__version__.py', NAME)

# Read the README file
with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()
    
#import __version__
exec(open(f'__version__.py').read())

setup(
    name=NAME,
    version=version,
    url="https://github.com/cumulus13/subdl",
    project_urls={
        "Documentation": "https://github.com/cumulus13/subdl",
        "Code": "https://github.com/cumulus13/subdl",
    },
    license="MIT License",
    author="cumulus13",
    author_email="cumulus13@gmail.com",
    maintainer="cumulus13 Team",
    maintainer_email="cumulus13@gmail.com",
    description="SubDL.com Downloader",
    long_description=readme,
    long_description_content_type="text/markdown",
    package_data={'subdl': ['*.ini', 'README.md', '__version__.py']}, 
    packages=[NAME],
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
    #data_files=['README.md', '__version__.py'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
    ],
    python_requires='>=3.6',
)
