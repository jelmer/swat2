#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='swat',
    version='0.1.1',
    description='',
    author='',
    author_email='',
    url='',
    install_requires=[
        "Pylons>=0.9.7",
        "PyYAML>=3.0.8",
        "Pam>=0.1.3",
        "repoze.who-friendlyform",
        "repoze.who"
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'swat': ['i18n/*/LC_MESSAGES/*.mo', '../who.ini', 'config/yaml/*.yaml']},
    message_extractors={'swat': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
            ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = swat.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
