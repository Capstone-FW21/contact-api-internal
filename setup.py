from setuptools import setup, find_packages

setup(
    description="Backend API for Contact Tracing, Capstone FW21",
    include_package_data=True,
    install_requires=["fastapi>=0.70.0", "uvicorn>=0.15.0", "ctdb_utility_lib>=0.1.8"],
    name="contact-api",
    packages=find_packages(),
    python_requires=">=3.5.0",
    version="0.1.1",
)
