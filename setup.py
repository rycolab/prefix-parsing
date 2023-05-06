from setuptools import setup

install_requires = [
    "numpy",
    "pytest",
]


setup(
    name="fastlri",
    install_requires=install_requires,
    version="0.1",
    scripts=[],
    packages=["fastlri"],
)
