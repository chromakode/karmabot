"""
An extension/facet for karmabot that will respond to queries for PSU CS course
informmation with information gathered by crawling cs.pdx.edu for said course
info. Depends on Beautiful Soup.
"""
from collections import OrderedDict
import time
from urllib import urlencode
from urllib2 import urlopen

from BeautifulSoup import BeautifulSoup

from karmabot.core.client import thing
from karmabot.core.thing import ThingFacet
from karmabot.core.register import facet_registry
from karmabot.core.commands.sets import CommandSet

#TODO:
#      Get rid of course command syntax? maybe?
#      Add error handing to webpage fetching.
#      Search with different keys.


@facet_registry.register
class ScheduleFacet(ThingFacet):
    """
    Class which implements the ThingFacet interface and provides the new
    karmabot course info reporting functionality.
    """
    name = "course"
    commands = thing.add_child(CommandSet(name))
    URL = "http://cs.pdx.edu/schedule/termschedule?"

    @commands.add(u"course {CSXXX} {TERM} {YEAR}",
                  u"Get course information from CS website.")
    def course(self, context, CSXXX, TERM, YEAR):
        """
        High level command handler for the course command. Manages
        course cache and recrawls if timeout is exceeded.
        """
        CSXXX = CSXXX.replace('CS', '').strip()
        sched_key = TERM + YEAR
        cur_time = time.time()
        response = ""
        _cls = ScheduleFacet
        defaults = {"ret_times": {}, "schedules": {}}

        if self.state:
            sched_state = self.state.get("cs_sched_state", defaults)
        else:
            self.state = dict()
            sched_state = defaults

        if cur_time - sched_state["ret_times"].get(sched_key, 0) > 3600:
            params = urlencode({"term": TERM, "year": YEAR})
            url = _cls.URL + params
            result_rows = _cls.apply_schema(_cls.scrape(url))
            sched_state["schedules"][sched_key] = result_rows
            sched_state["ret_times"][sched_key] = cur_time

        for course in sched_state["schedules"][sched_key]:
            if CSXXX in course["Course"]:
                nothanks = [u'Notes', u'Sec', u'', u'-']
                course_str = ' '.join(value
                                      for key, value in course.iteritems()
                                      if value not in nothanks
                                      and key not in nothanks)
                response = response + course_str + "\n"

        self.state.update({'cs_sched_state': sched_state})
        context.reply(response)

    @classmethod
    def does_attach(cls, thing):
        """Facet does attach. Return name to signify this."""

        return thing.name == "course"

    @classmethod
    def apply_schema(self, rows):
        schema = rows.pop(0)
        return [OrderedDict(zip(schema, row)) for row in rows]

    @classmethod
    def scrape(self, url):
        url_data = urlopen(url)
        soup = BeautifulSoup(url_data.read())
        table = soup.findAll('table')[1]
        result = []

        for row in table.findAll('tr'):
            tr_row = list()
            for td in row.findAll('td'):
                td_str = list()
                for td_sub in td.recursiveChildGenerator():
                    if (td_sub.string and td_sub.string.strip() is not u'' and
                        td_sub.string.strip() not in td_str):
                        td_str.append(td_sub.string.strip())

                if td_str not in tr_row:
                    tr_row.append(''.join(td_str))
            result.append(tr_row)

        return result
