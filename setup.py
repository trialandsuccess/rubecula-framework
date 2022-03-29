from setuptools import setup, find_packages

setup(
    name='rubecula',
    version='0.1.0',
    packages=['rubecula'],
    install_requires=[
        'twisted',
        'autobahn',
        'requests',
        'pyopenssl',
        'service_identity',
        'pyyaml',
        'jinja2',
        'andi',
    ],
)
