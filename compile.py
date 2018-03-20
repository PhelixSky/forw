# -*- coding: utf-8 -*-

from distutils.core import setup
from Cython.Build import cythonize


setup(
    name = 'Forward App',
    ext_modules = cythonize("Forw.py")
)