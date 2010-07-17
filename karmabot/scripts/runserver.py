import sys

from twisted.internet import reactor, ssl
from twisted.python import log

from karmabot.core.client import KarmaBotFactory
from karmabot.core.facets import (
    bot,
    description,
    help,
    irc as ircfacet,
    karma,
    name,
)


def main():
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options] channels")

    # IRC connection options
    parser.add_option("-s", "--server",
                      action="store", dest="server",
                      default="irc.freenode.net",
                      help="IRC server to connect to")
    parser.add_option("-p", "--port",
                      action="store", type="int", dest="port", default=None,
                      help="IRC server to connect to")
    parser.add_option("--ssl",
                      action="store_true", dest="ssl", default=False,
                      help="use SSL")
    parser.add_option("--password",
                      action="store", dest="password", default=None,
                      help="server password")
    parser.add_option("-n", "--nick",
                      action="store", dest="nick", default="karmabot",
                      help="nickname to use")
    # Bot options
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="enable verbose output")
    parser.add_option("-d", "--data",
                      action="store", dest="filename", default="karma.json",
                      help="karma data file name")
    parser.add_option("-t", "--trust",
                      action="append", dest="trusted", default=[],
                      help="trusted hostmasks")
    parser.add_option("-f", "--facets",
                      action="append", dest="facets", default=[],
                      help="additional facets to load")

    (options, channels) = parser.parse_args()

    if not channels:
        parser.error("You must supply some channels to join.")
    else:
        log.msg("Channels to join: %s" % channels)

    if options.verbose:
        log.startLogging(sys.stdout)

    if not options.port:
        options.port = 6667 if not options.ssl else 9999

    # FIXME: this needs to be replaced with a real facet manager
    for facet_path in options.facets:
        execfile(facet_path, globals())

    factory = KarmaBotFactory(options.filename, options.nick,
                              channels, options.trusted, options.password)
    if not options.ssl:
        reactor.connectTCP(options.server, options.port, factory)
    else:
        reactor.connectSSL(options.server, options.port,
                           factory, ssl.ClientContextFactory())
    reactor.run()

if __name__ == "__main__":
    main()
