from setuptools import setup

setup(
    name='rubecula',
    version='0.1.2',
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
        'rich',
    ],
)
