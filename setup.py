from setuptools import setup, find_packages


setup(
    name='cgccli-project',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click>=7.0',
        'requests>=2.21'
    ],
    entry_points='''
        [console_scripts]
        cgccli=cgccli:entry_point
    ''',
)
