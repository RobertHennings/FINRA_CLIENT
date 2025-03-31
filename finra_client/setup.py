from setuptools import setup, find_packages

# Structure of the setup file can be found here: https://github.com/pypa/sampleproject/blob/db5806e0a3204034c51b1c00dde7d5eb3fa2532e/setup.py
# Load the README file for the long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Load the about contents
about = {}
with open("ecbdata/__about__.py") as f:
    exec(f.read(), about)

# Load the required packages
with open("requirements.txt", encoding="utf-8") as f:
    install_requirements = f.read().splitlines()

setup(
    name="finra_client",
    version=about['__version__'],
    description=about['__about__'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=about['__url__'],
    author=about['__author__'],
    author_email=about['__email__'],
    license='MIT',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Athletes/Students/Researcher",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    keywords=about['__keywords__'],
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=install_requirements,
)
