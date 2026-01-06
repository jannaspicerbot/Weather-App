"""
Setup configuration for Weather App
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="weather-app",
    version="1.0.0",
    description="Ambient Weather data collection, processing, and visualization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Weather App Team",
    python_requires=">=3.8",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.31.0",
        "pandas>=2.0.0",
        "plotly>=5.18.0",
        "numpy>=1.24.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.0",
        "duckdb>=0.10.0",
        "apscheduler>=3.10.0",
        "structlog>=24.1.0",
        # Launcher/GUI dependencies
        "pystray>=0.19.0",
        "Pillow>=10.0.0",
    ],
    entry_points={
        'console_scripts': [
            'weather-app=weather_app.cli:cli',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
