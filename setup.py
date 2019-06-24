import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="upload-test",
    version="0.0.1",
    author="Mr.MagicMonkey",
    author_email="owenkuai@gmail.com",
    description="just a test",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/owen-kuai/upload",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)