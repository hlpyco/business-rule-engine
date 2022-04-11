import os
import setuptools

version = os.getenv('HLPY_BUSINESS_RULE_ENGINE_VERSION', '0.0.1')

setuptools.setup(
    name="hlpy_business_rule_engine",
    version=version,
    license='MIT',
    description="The hlpy business rule engine.",
    author="hlpy",
    author_email="hlpy-IT@hlpy.co",
    url='https://github.com/hlpy-co/business-rule-engine',
    download_url=f'https://github.com/hlpy-co/business-rule-engine/archive/{version}.tar.gz',
    packages=setuptools.find_packages(exclude=['tests/']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
