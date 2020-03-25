import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="beets-originquery",
    version="1.0.1",
    author="x1ppy",
    packages=['beetsplug'],
    author_email="",
    description="Integrates origin.txt metadata into beets MusicBrainz queries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/x1ppy/beets-originquery",
    python_requires='>=3.6',
    install_requires=[
        "beets>=1.5.0",
        "jsonpath-rw",
    ],
)
