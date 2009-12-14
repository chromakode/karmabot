import sys
import random
import re

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
from twisted.python import log

import thing
import command

from facets import karma, description, name

class Context(object):
    def __init__(self, who, where, bot):
        self.who = who
        self.where = where
        self._bot = bot
        self.replied = False
        
    def reply(self, msg):
        self._bot.msg(self.where, msg)
        self.replied = True

class KarmaBot(irc.IRCClient):
    affirmative_prefixes = ["Affirmative", "Alright", "Done", "K", "OK", "Okay", "Sure", "Yes"]
    huh_msgs = ["Huh?", "What?"]
    
    def connectionMade(self):
        self.nickname = self.factory.nick
        self.password = self.factory.password
        irc.IRCClient.connectionMade(self)
        self.things = thing.ThingStore(self.factory.filename)
        self.things.load()
        self.thing_command_parser = command.thing.compile()
        self.listen_parser = command.listen.compile()

    def connectionLost(self, reason):
        log.msg("Disconnected")
        irc.IRCClient.connectionLost(self, reason)
        self.things.save()

    def signedOn(self):
        log.msg("Connected")
        for channel in self.factory.channels:
            self.join_with_key(channel)

    def join_with_key(self, channel):
        if ":" in channel:
            channel, key = channel.split(":")
        else:
            key = None
        self.join(channel, key)

    def msg(self, user, message, length = None):
        # Force conversion from unicode to utf-8
        if type(message) is unicode:
            message = message.encode("utf-8")
        irc.IRCClient.msg(self, user, message, length)

    def privmsg(self, user, channel, msg):  
        log.msg("[{channel}] {user}: {msg}".format(channel=channel, user=user, msg=msg))
        msg = msg.decode("utf-8")
        nick = user.split("!", 1)[0]
        who = nick if channel == self.nickname else channel
        context = Context(nick, who, self)
        
        self.listen_parser.handle_command(msg, context, self.things)
        
        # Addressed (either in channel or by private message)
        command = None
        if msg.startswith(self.nickname):
            command = msg[len(self.factory.nick):].lstrip(" ,:").rstrip()
            if self.thing_command_parser.handle_command(command, context, self.things) == False:
                self.msg(who, random.choice(self.huh_msgs))
            else:
                if not context.replied:
                    self.tell_yes(who, nick)
            
        self.things.save()
                    
    def tell_yes(self, who, nick):
        self.msg(who, "{yesmsg}, {nick}.".format(yesmsg=random.choice(self.affirmative_prefixes), nick=nick))

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
                      action="store", dest="server", default="irc.freenode.net",
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

    (options, channels) = parser.parse_args()
    
    if not channels:
        parser.error("You must supply some channels to join.")
    
    if options.verbose:
        log.startLogging(sys.stdout)
        
    if not options.port:
        options.port = 6667 if not options.ssl else 9999
    
    factory = KarmaBotFactory(options.filename, options.nick, channels, options.trusted, options.password)
    if not options.ssl:
        reactor.connectTCP(options.server, options.port, factory)
    else:
        reactor.connectSSL(options.server, options.port, factory, ssl.ClientContextFactory())    
    reactor.run()

if __name__ == "__main__":
    main()
