import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="hnet",
    version="0.0.1",
    author="Frederick Hoyles",
    author_email="top@secret.com",
    description="A silly SR API app",
    long_description = long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/frehoy/hnet",
    packages=setuptools.find_packages(),
        classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    )

