"""
Setup script for BloodFlow AI
Run: pip install -e .
"""

from setuptools import setup, find_packages

setup(
    name="bloodflow-ai",
    version="1.0.0",
    description="AI-Based Predictive Blood Inventory Management System",
    author="Your Name",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "pydantic>=2.0.0",
        "scikit-learn>=1.3.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "joblib>=1.3.0",
        "python-multipart>=0.0.6",
        "requests>=2.31.0",
    ],
)
