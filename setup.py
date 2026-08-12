from setuptools import setup, find_packages

setup(
    name="nids",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "scapy>=2.5.0",
        "psycopg2-binary>=2.9.9",
        "python-dotenv>=1.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "ruff>=0.4.0",
            "black>=24.0.0",
        ],
    },
    python_requires=">=3.11",
)
