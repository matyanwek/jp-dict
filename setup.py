import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="jp-dict",
    version="0.4",
    description="A command line Japanese-English dictionary",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matyanwek/jp-dict",
    author="Gal Zeira",
    author_email="gal_zeira@protonmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["jp-dict = jp_dict:main"]},
    packages=setuptools.find_packages("src", exclude=["*.json"]),
    package_dir={"": "src"},
    # package_data={"": ["*.json"]},  # slow; build data files locally
    python_requires=">=3.10",
)
