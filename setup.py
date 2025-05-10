from setuptools import setup, find_packages

setup(
    name="evopy",
    version="0.1.0",
    description="Modularny asystent AI do automatyzacji kodu i środowisk Python",
    author="tom-sapletta-com",
    packages=["evopy"],
    install_requires=[
        "flask",
        "matplotlib",
        "openpyxl",
        "requests"
    ],
    python_requires=">=3.8",
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'evopy-cli=cli:main',
        ],
    },
)
