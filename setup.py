from setuptools import setup

setup(
    name="MistrasDTA",
    version="0.1.0",
    description="Read AEWin acoustic emissions binary data files",
    author="Dan Cogswell",
    author_email="cogswell@mit.edu",
    license="MIT",
    url="https://github.com/d-cogswell/MistrasDTA",
    py_modules=["MistrasDTA"],
    install_requires=["numpy"]
)
