"""
Karmabot
--------
A highly extensible IRC karma+information bot

Features include, thing storage, karma tracking

Links
`````

* `development version
  <http://github.com/chromakode/karmabot/zipball/master#egg=Karmabot-dev>`_
"""

from setuptools import setup, find_packages

setup(
    name="karmabot",
    version="dev",
    packages=find_packages(),
    namespace_packages=['karmabot'],
    include_package_data=True,
    author="Max Goodman",
    author_email="",
    description="A highly extensible IRC karma+information bot",
    long_description=__doc__,
      zip_safe=False,
    platforms='any',
    license='BSD',
    url='http://www.github.com/dcolish/cockerel',

    classifiers=[
        'Development Status :: 4 - Beta ',
        'Environment :: Console',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ',
        'Programming Language :: Python',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        ],

    entry_points={
        'console_scripts': [
            'karmabot=karmabot.scripts.runserver:main',
            'migrate=karmabot.scripts.migrate:main',
            'reinkarnate=karmabot.scripts.reinkarnate:main',
            ],
        },

    install_requires=[
        'pyopenssl',
        'twisted',
        ],
    )
