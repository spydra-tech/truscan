"""Setup configuration for llm_scan package."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llm-scan",
    version="1.0.0",
    author="Spydra",
    author_email="support@spydra.com",
    description="A Python-based code scanning tool for AI/LLM-specific vulnerabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/code-scan2",
    project_urls={
        "Bug Reports": "https://github.com/your-org/code-scan2/issues",
        "Source": "https://github.com/your-org/code-scan2",
        "Documentation": "https://github.com/your-org/code-scan2#readme",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.11",
    install_requires=[
        "semgrep>=1.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "llm-scan=llm_scan.runner:main",
        ],
    },
    include_package_data=True,
    package_data={
        "llm_scan": [
            "rules/**/*.yaml",
            "rules/**/*.yml",
        ],
    },
)
