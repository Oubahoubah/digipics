from importlib.metadata import entry_points
from setuptools import setup

setup(
    name="digipics",
    version="0.1",
    description="Handle your digital pictures",
    url="http://gitlab.com",
    author="Stephan Skrodzki",
    author_email="skrodzki@stevekist.de",
    license="GNU Affero General Public License v3",
    packages=["digipics"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
    entry_points = { 'console_scripts' : ['digiimport=digipics.digiimport:main', 'digiphone=digipics.digiphone:main'] },
)
