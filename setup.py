from setuptools import find_packages, setup

setup(
    name="pynlp5",
    version="0.0.1",
    description="Fifth exercise of the Python programming course",
    author="Adam Kovacs",
    author_email="adam.kovacs@tuwien.ac.at",
    license="MIT",
    install_requires=["streamlit", "flask", "more_itertools", "tqdm", "matplotlib"],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    zip_safe=False,
)
