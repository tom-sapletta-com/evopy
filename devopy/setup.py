from setuptools import setup, find_packages

setup(
    name="devopy",
    version="0.1.0",
    description="Modularny asystent AI do automatyzacji kodu i środowisk Python",
    author="tom-sapletta-com",
    packages=find_packages(),
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
            'devopy-cli=cli:main',
        ],
    },
)
