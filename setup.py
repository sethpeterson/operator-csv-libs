from setuptools import setup, find_packages

setup(
    name='olm_management',
    version='0.0.1',
    description='Code to manage OLM related CSVs and channels',
    author='bennett-white',
    url='https://github.com/bennett-white/python-lib',
    packages=['olm_management'],
    install_requires=[
        'pyyaml',
        'pygithub',
        'dohq-artifactory',
        'slack_log_handler',
        'requests'
    ]
)