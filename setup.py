from setuptools import setup, find_packages

setup(
    name="network_monitoring",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # Dependencies will be installed from requirements.txt
    ],
    python_requires=">=3.8",
)
