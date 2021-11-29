__version__ = '0.1.1'

_classifiers = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Topic :: Software Development :: Libraries',
    'Topic :: Utilities',
]

def _run_setup():
    from setuptools import setup

    setup(
        name='xled_plus',
        version=__version__,
        author='Anders Holst',
        author_email='anders.holst@ri.se',
        url='https://github.com/Anders-Holst/xled_plus',
        packages=['xled_plus'],
        description='Addons to the XLED package for controling Twinkly LED lights',
        long_description='Addons to the XLED package for controling Twinkly LED lights',
        license='MIT',
        classifiers=_classifiers,
        keywords=['xled','twinkly','light-effects'],
        install_requires=['xled'],
    )


if __name__ == '__main__':
    _run_setup()
