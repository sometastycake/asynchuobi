import setuptools
from setuptools import setup

requirements = [
    "aiohttp>=3.8.3",
    "pydantic>=1.10.2"
]


setup(
    name='asynchuobi',
    version='0.0.1',
    url='https://github.com/sometastycake/asynchuobi',
    license='MIT',
    author='Mike M',
    author_email='stopthisworldplease@outlook.com',
    description='Unofficial asynchronous python client for Huobi cryptoexchange',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(exclude=['tests']),
    zip_safe=False,
    python_requires='>=3.7',
    install_requires=requirements,
    setup_requires=requirements,
    include_package_data=True,
)
