import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="hnet",
    version="0.0.1",
    author="Frederick Hoyles",
    author_email="top@secret.com",
    description="An app wow",
    long_description = long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/frehoy/ogdata",
    packages=setuptools.find_packages(),
        classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    )

