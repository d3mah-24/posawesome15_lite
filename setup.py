# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

# No external dependencies required - frappe and erpnext are managed by bench
install_requires = []

# get version from __version__ variable in posawesome/__init__.py
from posawesome import __version__ as version

setup(
    name="posawesome",
    version=version,
    description="posawesome",
    author="future-support",
    author_email="abdopcnet@gmail.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
