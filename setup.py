from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="MistrasDTA",
    version="0.1.0",
    description="Read AEWin acoustic emissions binary data files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dan Cogswell",
    author_email="cogswell@mit.edu",
    license="MIT",
    url="https://github.com/d-cogswell/MistrasDTA",
    py_modules=["MistrasDTA"],
    install_requires=["numpy"]
)
