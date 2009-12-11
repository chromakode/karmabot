import sys
import random
import re
import time

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
from twisted.python import log

try:
    import json
except ImportError:
    import simplejson as json

def created_timestamp(who, where):
    return {"who":who, "when":time.time(), "where":where}
    
def bold(text):
    return u"\u0002{0}\u000F".format(text)

class KarmaData:
    def __init__(self, filename):
        self.filename = filename
        self.data = None
        
    def load(self):
        try:
            self.data = json.load(open(self.filename))
        except IOError:
            self.data = {"things":{}}

    def save(self):
        json.dump(self.data, open(self.filename, "w"), sort_keys=True, indent=4)
        
    @property
    def things(self):
        return self.data["things"]
        
    def get_thing(self, name, who=None, where=None):
        name = name.strip()
        key = name.lower()
        if not key in self.things:
            self.things[key] = {"name":name, "desc":[], "karma":0, "created":created_timestamp(who, where)}
            
        return self.things[key]

class KarmaBot(irc.IRCClient):

    karma_re = re.compile(r"""(?:
                                (\S+)        # Short form thing
                                |            # --or--
                                (?:\((.+)\)) # Long form thing (in parens)
                              )
                              (\+\+|--)      # ++ or --""", re.X | re.U)
                              
    affirmative_prefixes = ["Affirmative", "Alright", "Done", "K", "OK", "Okay", "Sure", "Yes"]
    huh_msgs = ["Huh?", "What?"]
    
    def connectionMade(self):
        self.nickname = self.factory.nick
        self.password = self.factory.password
        irc.IRCClient.connectionMade(self)
        self.karma = KarmaData(self.factory.filename)
        self.karma.load()

    def connectionLost(self, reason):
        log.msg("Disconnected")
        irc.IRCClient.connectionLost(self, reason)
        self.karma.save()

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
        
        # Listen for karma adjustments in messages
        for match in self.karma_re.finditer(msg):
            short_name, long_name, op = match.groups()
            thing_name = short_name or long_name
            thing = self.karma.get_thing(thing_name, user, channel)
            if op == "++":
                thing["karma"] += 1
            else:
                thing["karma"] -= 1
            log.msg("({name){op}".format(name=repr(thing_name), op=op))
        msg = msg.replace("++","").replace("--","")
        
        # Try to find a command in the message
        command = None
        
        # Addressed (either in channel or by private message)
        if msg.startswith(self.nickname):
            command = msg[len(self.factory.nick):].lstrip(" ,:").rstrip()
            who = user if channel == self.nickname else channel
        
        if command:
            log.msg("Command from {who} by {user}: {cmd}".format(who=who, user=user, cmd=repr(command)))
            
            # Queries
            if command.lower() in self.karma.things:
                self.tell_about(who, command)
                return

            # Descriptions
            thing_name, sep, desc = command.partition(" is ")
            if thing_name and desc:
                thing = self.karma.get_thing(thing_name, user, channel)
                if desc.startswith("<reply>"):
                    thing["desc"].append({"created":created_timestamp(user, channel), "text":desc[len("<reply>"):], "reply":True})
                else:
                    thing["desc"].append({"created":created_timestamp(user, channel), "text":desc})
                self.tell_yes(who, nick)
                return
            
            # Join/leave commands
            call, sep, args = command.partition(" ")
            if call == "join":
                self.join_with_key(args.encode("utf-8"))
                self.tell_yes(who, nick)
                return
            elif call == "leave":
                self.tell_yes(who, nick)
                self.leave(args.encode("utf-8"))
                return
            
            if user in self.factory.trusted:
                if call == "save!":
                    self.karma.save()
                    self.tell_yes(who, nick)
                    return
                elif call == "reload!":
                    self.karma.load()
                    self.tell_yes(who, nick)
                    return
                elif call == "quit!":
                    self.tell_yes(who, nick)
                    reactor.iterate()
                    reactor.stop()
                    return
            
            # If we got to here, no suitable command was found.
            self.msg(who, random.choice(self.huh_msgs))        
                    
    def tell_yes(self, who, nick):
        self.msg(who, "{yesmsg}, {nick}.".format(yesmsg=random.choice(self.affirmative_prefixes), nick=nick))     
                
    def tell_about(self, who, what):
        if what.lower() in self.karma.things:
            log.msg("Telling {who} about {what}".format(who=who, what=repr(what)))
            thing = self.karma.get_thing(what)
            
            replies = (desc["text"] for desc in thing["desc"]
                       if "reply" in desc and desc["reply"]==True)
            for reply in replies:
                self.msg(who, reply)
            
            desc = ", ".join(desc["text"] for desc in thing["desc"]
                            if "reply" not in desc or desc["reply"]==False)
            if desc or thing["karma"] != 0:
                self.msg(who, "{name}({karma}): {desc}".format(
                    name  = bold(thing["name"]),
                    desc  = desc+" " if desc else "",
                    karma = thing["karma"])
                )
        else:
            self.msg(who, random.choice(self.huh_msgs))

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
