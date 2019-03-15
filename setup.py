from setuptools import setup, find_packages


setup(
    name='cgccli',
    version='1.7',
    author='Marko Jelenkovic',
    author_email='jelenko555@gmail.com',
    descripton='CLI tool for CGC Public API',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click>=7.0',
        'requests>=2.21'
    ],
    py_modules=['cgccli', 'api_urls', 'cli_exceptions'],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Code Generators',
        'Intended Audience :: Developers',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Utilities'
    ],
    entry_points='''
        [console_scripts]
        cgccli=cgccli:entry_point
    '''
)
