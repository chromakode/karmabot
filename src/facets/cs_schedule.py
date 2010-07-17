import time
import urllib
from BeautifulSoup import BeautifulSoup

import thing
import command

#TODO:
#      Get rid of course command syntax? maybe?
#      Add error handing to webpage fetching.
#      Allow term specification.
#      Search with different keys.

@thing.facet_classes.register
class ScheduleFacet(thing.ThingFacet):
    name = "course"
    commands = command.thing.add_child(command.FacetCommandSet(name))
    URL = "http://cs.pdx.edu/schedule/termschedule?"
    SECONDS_PER_HOUR = 60 * 60
    #TODO should probably go in __init__ but that didnt compile.
    last_retrieval_time = {}
    sched = {}

    @commands.add(u"{thing} {string}", help=u"Get course information.")
    def course1(self, thing, string, context):
        term = "Fall"
        year = "2010"
        sched_key = term + year
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
        cur_time = time.time()
        if cur_time - self.last_retrieval_time.get(sched_key, 0) > self.SECONDS_PER_HOUR:
            self.sched[sched_key] = self.parse_table(self.get_table(self.retrieve_page(term, year)))
            self.last_retrieval_time[sched_key] = cur_time
        response = ""
        for course in self.sched[sched_key]:
            if course["Course"] == string:
                response = response + format_course(course) + "\n"
        context.reply(response)

    @classmethod
    def does_attach(cls, thing):
        return thing.name == "course"
    
    @classmethod
    def retrieve_page(cls, term, year):
        params = urllib.urlencode({"term": term, "year": year})
        page = urllib.urlopen(cls.URL + params)
        return page.read()

    @classmethod
    def get_table(cls, page):
        soup = BeautifulSoup(page)
        table = soup.find(**{"class": "userpage"}).table
        rows = table.findAll("tr")
        return rows

    @classmethod
    def parse_table(cls, table):
        def find_content(item):
            if item.small == None:
                return None
            elif item.small.string == None and item.small.a == None:
                return None
            elif item.small.string == None and item.small.a != None:
                return item.small.a.string
            elif len(item.contents) > 2 and item.contents[1] == u"-":
                return u"-".join(map(lambda x: x.string, item.findAll("small")))
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
