from setuptools import setup, find_packages

setup(
    name="socialutils",
    version="1.0.0",
    author="Juan M Beccaceci",
    author_email="juanbeccaceci@icloud.com",
    description="Fast and lightweight utility functions for social media management",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JBeccaceci/socialutils",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
