from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="remocon-for-adb",
    version="0.1.0",
    author="TE-TakashiAMori",
    author_email="takashi.a.mori@sony.com",
    description="Android TV Remote Control via ADB for Ubuntu",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TE-TakashiAMori/TvRemoconForADB",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "remocon-adb=remocon_for_adb.presentation.cli.main:main",
            "remocon-adb-gui=remocon_for_adb.presentation.gui.main_window:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
