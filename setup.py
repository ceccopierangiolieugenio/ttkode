from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

version = "__VERSION__"
name = "__NAME__"

print(f"Version: {version}")
print(f"Name: {name}")

setup(
    name=name,
    version=version,
    author='Eugenio Parodi',
    author_email='ceccopierangiolieugenio@googlemail.com',
    description='Terminal ToolKit Studio Code editor',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ceccopierangiolieugenio/ttkode",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Terminals",
        "Topic :: Software Development :: User Interfaces"],
    include_package_data=False,
    packages=['ttkode','ttkode.app'],
    python_requires=">=3.8",
    install_requires=[
        'pyTermTk>=0.9.0a43',
        'appdirs',
        'pyyaml',
        'pygments'],
    entry_points={
        'console_scripts': [
            'ttkode = ttkode:main',
        ],
    },
)