import time
import urllib
from BeautifulSoup import BeautifulSoup

from karmabot.core.client import thing
from karmabot.core.thing import ThingFacet
from karmabot.core.register import facet_registry, presenter_registry
from karmabot.core.commands.sets import CommandSet

#TODO:
#      Get rid of course command syntax? maybe?
#      Add error handing to webpage fetching.
#      Search with different keys.

@facet_registry.register
class ScheduleFacet(ThingFacet):
    name = "course"
    commands = thing.add_child(CommandSet(name))
    URL = "http://cs.pdx.edu/schedule/termschedule?"

    @commands.add(u"course {CSXXX} {TERM} {YEAR}", u"Get course information from CS website.")
    def course1(self, context, CSXXX, TERM, YEAR):
        SECONDS_PER_HOUR = 60 * 60
        sched_key = TERM + YEAR
        def to_str(item):
            if item is None:
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
        if self.state is None:
            self.state = {}
        state = self.state.get("cs_sched_state", {"ret_times": {}, "schedules": {}})

        cur_time = time.time()
        if cur_time - state["ret_times"].get(sched_key, 0) > SECONDS_PER_HOUR:
            state["schedules"][sched_key] = ScheduleFacet.parse_table(ScheduleFacet.get_table(ScheduleFacet.retrieve_page(TERM, YEAR)))
            state["ret_times"][sched_key] = cur_time
        response = ""
        for course in state["schedules"][sched_key]:
            if course["Course"] == CSXXX:
                response = response + format_course(course) + "\n"
        context.reply(response)
        self.state["cs_sched_state"] = state

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
            if item.small is None:
                return None
            elif item.small.string is None and item.small.a is None:
                return None
            elif item.small.string is None and item.small.a is not None:
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
