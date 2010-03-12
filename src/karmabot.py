import sys
import random

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, task, ssl
from twisted.python import log

import thing
import command

VERSION = "0.2"


class Context(object):

    def __init__(self, user, where, bot):
        self.user = user
        self.where = where
        self.bot = bot
        self.replied = False

    @property
    def nick(self):
        return self.user.split("!", 1)[0]

    @property
    def who(self):
        return self.nick

    def reply(self, msg, where=None, replied=True):
        if not where:
            where = self.where

        self.bot.msg(where, msg)
        self.replied = replied


class KarmaBot(irc.IRCClient):
    affirmative_prefixes = [u"Affirmative", u"Alright", u"Done",
                            u"K", u"OK", u"Okay", u"Sure", u"Yes"]
    huh_msgs = [u"Huh?", u"What?"]

    def connectionMade(self):
        self.nickname = self.factory.nick
        self.password = self.factory.password
        irc.IRCClient.connectionMade(self)
        self.init()
        
    def init(self):
        self.things = thing.ThingStore(self.factory.filename)
        self.things.load()
        self.command_parser = command.thing.compile()
        self.listen_parser = command.listen.compile()
        
        self.save_timer = task.LoopingCall(self.save)
        self.save_timer.start(60.0*5, now=False)

    def connectionLost(self, reason):
        log.msg("Disconnected")
        self.things.save()
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        log.msg("Connected")
        for channel in self.factory.channels:
            self.join_with_key(channel)

    def join_with_key(self, channel):
        if ":" in channel:
            channel, key = channel.split(":")
        else:
            key = None
        log.msg("Joining {0}".format(channel))
        self.join(channel, key)

    def save(self):
        log.msg("Saving data")
        self.things.save()

    def topicUpdated(self, user, channel, newTopic):
        thing = self.things.get_thing(channel, Context(user, channel, self))
        thing.facets["ircchannel"].topic = newTopic

    def msg(self, user, message, length=None):
        # Force conversion from unicode to utf-8
        if type(message) is unicode:
            message = message.encode("utf-8")

        for line in message.split("\n"):
            irc.IRCClient.msg(self, user, line, length)

    def privmsg(self, user, channel, msg):
        log.msg("[{channel}] {user}: {msg}".format(channel=channel,
                                                   user=user, msg=msg))
        msg = msg.decode("utf-8")
        where = self.nickname if channel == self.nickname else channel
        context = Context(user, where, self)

        listen_handled, msg = self.listen_parser.handle_command(msg, context)

        # Addressed (either in channel or by private message)
        command = None
        if msg.startswith(self.nickname):
            command = msg[len(self.factory.nick):].lstrip(" ,:").rstrip()
            if not self.command_parser.handle_command(command, context)[0]:
                self.msg(where, random.choice(self.huh_msgs))
            else:
                if not context.replied:
                    self.tell_yes(where, context.nick)

    def tell_yes(self, who, nick):
        self.msg(who, u"{yesmsg}, {nick}.".format(
                yesmsg=random.choice(self.affirmative_prefixes), nick=nick))


class KarmaBotFactory(protocol.ClientFactory):
    protocol = KarmaBot

    def __init__(self, filename, nick, channels, trusted, password=None):
        self.nick = nick
        self.channels = channels
        self.filename = filename
        self.trusted = trusted
        self.password = password

    def clientConnectionLost(self, connector, reason):
        # FIXME: Infinite reconnects are bad
        #connector.connect()
        pass

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()


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
    from facets import bot, karma, description, name, help, irc as ircfacet
    main()
