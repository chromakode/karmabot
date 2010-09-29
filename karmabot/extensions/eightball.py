# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
from karmabot import thing
from  karmabot import command
import random

predictions = [ "As I see it, yes",
		"It is certain",
		"It is decidedly so",
		"Most likely",
		"Outlook good",
		"Signs point to yes",
		"Without a doubt",
		"Yes",
		"Yes - definitely",
		"You may rely on it",
		"Reply hazy, try again",
		"Ask again later",
		"Better not tell you now",
		"Cannot predict now",
		"Concentrate and ask again",
		"Don't count on it",
		"My reply is no",
		"My sources say no",
		"Outlook not so good",
		"Very doubtful"]

@thing.facet_classes.register
class EightBallFacet(thing.ThingFacet):
    name = "eightball"    
    commands = command.thing.add_child(command.FacetCommandSet(name))
    
    @classmethod
    def does_attach(cls, thing):
        return thing.name == "eightball"  
    
    @commands.add("shake {thing}", help="shake the magic eightball")
    def shake(self, thing, context):
        context.reply(random.choice(predictions) + ".")
