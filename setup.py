from setuptools import setup
from Cython.Build import cythonize
from distutils.core import Extension

# 指定語言
extensions = [
    Extension("GetThreadContext", ["GetThreadContext.pyx"])
]

setup(
    ext_modules=cythonize("GetThreadContext.pyx"),
    zip_safe=False,
)