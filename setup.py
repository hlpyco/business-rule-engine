import os
import setuptools

version = os.getenv('HLPY_BUSINESS_RULE_ENGINE_VERSION', '0.0.1')

setuptools.setup(
    name="hlpy_business_rule_engine",
    version=version,
    author="hlpy",
    author_email="info@hlpy.co",
    description="The hlpy business rule engine.",
    packages=setuptools.find_packages(exclude=['tests/']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
