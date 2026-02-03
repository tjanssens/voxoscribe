"""Setup script for VoxoScribe."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="voxoscribe",
    version="1.0.0",
    author="VoxoScribe Team",
    description="Your voice, transcribed locally",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/voxoscribe",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
    python_requires=">=3.11",
    install_requires=[
        "faster-whisper>=1.0.0",
        "sounddevice>=0.4.6",
        "numpy>=1.24.0",
        "pystray>=0.19.4",
        "pillow>=10.0.0",
        "pynput>=1.7.6",
        "pyperclip>=1.8.2",
    ],
    entry_points={
        "console_scripts": [
            "voxoscribe=src.main:main",
        ],
    },
)
