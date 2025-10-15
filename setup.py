# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

# No external dependencies required - frappe and erpnext are managed by bench
install_requires = []

# get all values from hooks.py
from posawesome.hooks import app_publisher, app_email, app_name, version

setup(
    name=app_name,
    version=version,
    description=app_name,
    author=app_publisher,
    author_email=app_email,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
