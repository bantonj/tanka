from BeautifulSoup import BeautifulSoup, NavigableString
import urllib
import json
from pyopenkeyval import pyopenkeyval
from decimal import Decimal

#TODO:
    #Need to make the urlopen return something if it fails, this would mean it is offline


teams = [u'Toronto', u'Philadelphia', u'Boston', u'New York', u'Brooklyn', u'Indiana', u'Chicago', u'Detroit', u'Cleveland', u'Milwaukee', u'Miami', u'Atlanta', u'Charlotte', u'Washington', 
         u'Orlando', u'Portland', u'Oklahoma City', u'Denver', u'Minnesota', u'Utah', u'L.A. Clippers', u'Golden State', u'L.A. Lakers', u'Phoenix', u'Sacramento', u'San Antonio', u'Houston',
         u'Dallas', u'Memphis', u'New Orleans']

"""[wins, losses, win_per, gamesback, conference, division, home]"""

class NBAStatsParser(object):
    def __init__(self, mspaceurl=None):
        if not mspaceurl:
            self.mspaceurl = "http://www.nba.com/standings/team_record_comparison/conferenceNew_Std_Div.html?ls=iref:nba:gnav"
        else:
            self.mspaceurl = mspaceurl
    
    def gethtml(self):
        try:
            htmldata = urllib.urlopen(self.mspaceurl)
        except IOError as e:
            print e
            return False
        return htmldata
        
    def parse(self):
        htmldata = self.gethtml()
        if not htmldata:
            return False
        soup = BeautifulSoup(htmldata)
        tds = soup.findAll('table', 'genStatTable mainStandings')
        #ebno = tds[4].contents[1].contents[0].contents[0]
        getnow = False
        getcount = 0
        gotlist = []
        teamnow = ''
        teamnow_dict = {}
        stat_order = ['won', 'lost', 'win_percentage', 'gamesback', 'conference', 'division', 'home', 'road', 'last10', 'streak']
        for x in tds[0].contents:
            if not isinstance(x, NavigableString):
                for y in x.contents:
                    if not isinstance(y, NavigableString):
                        for z in y.contents:
                            if not isinstance(z, NavigableString):
                                if len(z.contents) > 0 and z.contents[0] in teams:
                                    getnow = True
                                    teamnow = z.contents[0]
                            elif getnow:
                                if getcount == 0:
                                    teamnow_dict = {'name':teamnow}
                                teamnow_dict[stat_order[getcount]]= self.parse_value(z, stat_order[getcount])
                                getcount += 1
                                if getcount == 9:
                                    gotlist.append(teamnow_dict)
                                    getnow = False
                                    getcount = 0
                                    teamnow_dict = {}
        return json.dumps(gotlist)
        
    def parse_value(self, val, stat_name):
        if stat_name == 'won' or stat_name == 'lost':
            return int(val)
        elif stat_name == 'last10':
            if val.split('-')[0] == '10':
                return 1.0
            return str(Decimal(float(val.split('-')[0])/(float(val.split('-')[1])+float(val.split('-')[0]))).quantize(Decimal('.001')))
        else:
            return val
        

if __name__ == "__main__":
    nbaer = NBAStatsParser()
    json_stats = nbaer.parse()
    okv = pyopenkeyval()
    result = okv.store('nbastats-dknxhsywe6465egdhuiq874yqaAAw1', json_stats)
    print result
    
    