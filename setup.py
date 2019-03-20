from setuptools import find_packages, setup

setup(
    name='flask_api_project',
    version='0.0.1',
    description="libs for neoline api projects",
    author='neoline',
    author_email='xx@xx.com',
    packages=find_packages(exclude=[]),
    install_requires=[],
    zip_safe=True,
    entry_points='''
        [console_scripts]
        flask_api_project=flask_api_project.cli.main:cli
    '''
)
