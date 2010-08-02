import random

from twisted.words.protocols import irc
from twisted.internet import reactor, task
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.python import log

from .thing import ThingStore
from .commands.sets import CommandSet

VERSION = "0.2"

listen = CommandSet("listen")
thing = CommandSet("thing", regex_format="(^{0}$)")


class Context(object):

    def __init__(self, user, where, bot, priv=False):
        self.user = user
        self.where = where
        self.bot = bot
        self.replied = False
        self.private = priv

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
        self.things = ThingStore(self.factory.filename)
        self.things.load()
        self.command_parser = thing.compile()
        self.listen_parser = listen.compile()

        self.save_timer = task.LoopingCall(self.save)
        self.save_timer.start(60.0 * 5, now=False)

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

    def msg(self, user, message, length=160):
        # Force conversion from unicode to utf-8
        if type(message) is unicode:
            message = message.encode("utf-8")

        for line in message.split("\n"):
            irc.IRCClient.msg(self, user, line, None)

    def privmsg(self, user, channel, msg):
        log.msg("[{channel}] {user}: {msg}".format(channel=channel,
                                                   user=user, msg=msg))
        msg = msg.decode("utf-8")

        context = Context(user, channel, self)
        context.priv = True if (channel == self.nickname and
                                context.nick != self.nickname) else False

        listen_handled, msg = self.listen_parser.handle_command(msg, context)

        # Addressed (either in channel or by private message)
        command = None
        if msg.startswith(self.nickname) or context.priv:
            if not context.priv:
                command = msg[len(self.factory.nick):].lstrip(" ,:").rstrip()
            else:
                context.where = context.nick
                command = msg.rstrip()
            if not self.command_parser.handle_command(command, context)[0]:
                self.msg(channel, random.choice(self.huh_msgs))
            else:
                if not context.replied:
                    self.tell_yes(channel, context.nick)

    def tell_yes(self, who, nick):
        self.msg(who, u"{yesmsg}, {nick}.".format(
                yesmsg=random.choice(self.affirmative_prefixes), nick=nick))


class KarmaBotFactory(ReconnectingClientFactory):
    protocol = KarmaBot

    def __init__(self, filename, nick, channels, trusted, password=None):
        self.nick = nick
        self.channels = channels
        self.filename = filename
        self.trusted = trusted
        self.password = password

    def buildProtocol(self, addr):
        # Reset the ReconnectingClientFactory reconnect delay because we don't
        # want the next disconnect to force karmabot to delay forever.
        self.resetDelay()
        return ReconnectingClientFactory.buildProtocol(self, addr)

    def clientConnectionLost(self, connector, reason):
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()
