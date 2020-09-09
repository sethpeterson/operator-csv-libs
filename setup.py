from setuptools import setup, find_packages

setup(
    name='operator-csv-libs',
    version='0.0.2',
    description='Code to manage OLM related CSVs and channels',
    author='bennett-white',
    url='https://github.com/multicloud-ops/operator-csv-libs',
    packages=['operator-csv-libs'],
    install_requires=[
        'pyyaml',
        'pygithub',
        'dohq-artifactory',
        'slack_log_handler',
        'requests'
    ]
)