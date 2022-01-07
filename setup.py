import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="webxpath",  # Replace with your own username
    version="0.0.2",
    author="Shiplu Mokaddim",
    author_email="shiplu@mokadd.im",
    description="Run XPath query and expressions against websites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shiplu/webxpath",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License 2.0",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["lxml", "prettytable", "requests", "jq", "html2text"],
)
