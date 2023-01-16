from setuptools import find_packages, setup

setup(
    name="quicksilver",
    version="0.1",
    description="API for avatar.jairtrejo.com",
    url="https://avatar.jairtrejo.com",
    author="Jair Trejo",
    author_email="jair@jairtrejo.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "attrs>=19.3.0",
        "inflection>=0.4.0",
        "PyJWT>=1.7.1",
        "structlog>=20.1.0",
    ],
    extras_require={
        "dev": [
            "aws-sam-cli>=0.51.0",
            "awscli>=1.18.66",
            "black>=19.10b0",
            "boto3>=1.13.16",
            "colorama>=0.4.3",
            "coverage>=5.1",
            "flake8>=3.8.2",
            "pytest>=7.2.1",
            "isort>=5.11.4",
        ]
    },
    zip_safe=False,
)
