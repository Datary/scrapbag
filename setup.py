import os
import sys
from setuptools import setup, find_packages
from pip._internal.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session=False)
required = [str(ir.req) for ir in install_reqs]

_here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, _here)


def version():
    import imp
    path = os.path.join(_here, 'scrapbag', 'version.py')
    mod = imp.load_source('version', path)
    return mod.__version__

setup(
    name='scrapbag',
    packages=find_packages(),
    package_data={'data-aux': ['*']},
    include_package_data=True,
    version=version(),
    description='Scrapbag Python lib',
    author='Datary developers team',
    author_email='support@datary.io',
    url='https://github.com/Datary/scrapbag',
    download_url='https://github.com/Datary/scrapbag',
    keywords=[
        'scrapman',
        'scrapbag',
        'utils',
        'datary',
        'scrapping'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    install_requires=required,
)
