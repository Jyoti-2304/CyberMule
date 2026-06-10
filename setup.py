from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bank-fraud-detection",
    version="0.1.0",
    author="Bank Fraud Detection Team",
    author_email="fraud-detection@bank.com",
    description="AI/ML solution for detecting suspicious transactions and mule accounts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "fraud-api=src.api.main:main",
            "fraud-processor=src.real_time_processing.kafka_processor:main",
        ],
    },
)
