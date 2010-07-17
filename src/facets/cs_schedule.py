import urllib
from BeautifulSoup import BeautifulSoup

URL = "http://cs.pdx.edu/schedule/termschedule?"

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

if __name__ == "__main__":
    table = get_table(retrieve_page("Fall", "2010"))
    print parse_table(table)
