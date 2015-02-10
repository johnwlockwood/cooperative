import uuid
import os
import sys

try:
    from setuptools import find_packages
    from setuptools import setup
    packages = find_packages()
except ImportError:
    from distutils.core import setup
    packages = ['cooperative']

from pip.req import parse_requirements

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


def read(fname):
    """
    Open and read a filename in this directory.
    :param fname: `str` file name in this directory

    Returns contents of file fname
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_version():
    import imp

    with open('cooperative/_meta.py', 'rb') as fp:
        mod = imp.load_source('_meta', 'cooperative', fp)

    return mod.version


def get_requirements(filename):
    reqs = parse_requirements(filename, session=uuid.uuid1())

    return [str(r.req) for r in reqs]


def get_install_requires():
    return get_requirements('requirements.txt')


def get_test_requires():
    return get_requirements('requirements_dev.txt')


try:
    license_info = open('LICENSE').read()
except:
    license_info = 'APACHE 2.0'

setup_args = dict(
    name="cooperative",
    version=get_version(),
    author="John W Lockwood IV",
    author_email="john@tackletronics.com",
    description=("Write computationally intensive "
                 "non-blocking code without callbacks"),
    license=license_info,
    keywords="data",
    url="https://github.com/johnwlockwood/cooperative",
    package_dir={'cooperative': 'cooperative'},
    packages=packages,
    install_requires=get_install_requires(),
    tests_require=get_test_requires(),
    long_description=read('README.md'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)

if __name__ == '__main__':
    setup(**setup_args)
