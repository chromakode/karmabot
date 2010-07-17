__import__('pkg_resources').declare_namespace(__name__)

from .core import (
    client,
    commands,
    facets,
    ircutils,
    thing,
    register,
    utils,
)

__all__ = ['client', 'commands', 'facets', 'ircutils',
           'thing', 'register', 'utils']
