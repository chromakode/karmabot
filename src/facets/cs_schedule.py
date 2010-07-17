import urllib
from BeautifulSoup import BeautifulSoup

import thing
import command
import random

#TODO: Put everything into the class.
#      Fix time bug.
#      Get rid of course command syntax? maybe?
#      Add error handing to webpage fetching.
#      Allow term specification.
#      Search with different keys.
#      Save page parsing results update every hour/day/etc.
URL = "http://cs.pdx.edu/schedule/termschedule?"

@thing.facet_classes.register
class ScheduleFacet(thing.ThingFacet):
    name = "course"
    commands = command.thing.add_child(command.FacetCommandSet(name))
    
    @classmethod
    def does_attach(cls, thing):
        return thing.name == "course"
    
    @commands.add(u"{thing} {string}", help=u"Get course information.")
    def course1(self, thing, string, context):
        def to_str(item):
            if item == None:
                return ""
            else:
                return item + " "
        def format_course(course):
            return to_str(course["CRN"]) +\
                   to_str(course["Title"]) +\
                   to_str(course["Faculty"]) +\
                   to_str(course["Days"]) +\
                   to_str(course["Time"]) +\
                   to_str(course["Bldg"]) +\
                   to_str(course["Room"])
        sched = parse_table(get_table(retrieve_page("Fall", "2010")))
        response = ""
        for course in sched:
            if course["Course"] == string:
                response = response + format_course(course) + "\n"
        context.reply(response)

def retrieve_page(term, year):
    params = urllib.urlencode({"term": term, "year": year})
    page = urllib.urlopen(URL + params)
    return page.read()

def get_table(page):
    soup = BeautifulSoup(page)
    table = soup.find(**{"class": "userpage"}).table
    rows = table.findAll("tr")
    return rows

def parse_table(table):
    def find_content(item):
        if item.small == None:
            return None
        elif item.small.string == None and item.small.a == None:
            return None
        elif item.small.string == None and item.small.a != None:
            return item.small.a.string
        else:
            return item.small.string
    master_list = []
    columns = table[0].findAll("small")
    columns = map(lambda x: x.string.strip(), columns)
    for row in table[1:]:
        row = row.findAll("td")
        row = map(find_content, row)
        class_dict = dict(zip(columns, row))
        course = u"".join(class_dict[u"Course"].split()[0:2])
        class_dict[u"Title"] = class_dict[u"Course"]
        class_dict[u"Course"] = course
        master_list.append(class_dict)
    return master_list
