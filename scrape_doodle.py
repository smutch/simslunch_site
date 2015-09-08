from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import json
import datetime

def _next_weekday(d, weekday):
    """http://stackoverflow.com/a/6558571"""
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def scrape_doodle():
    soup = BeautifulSoup(urlopen("http://doodle.com/poll/g3idnd5gfg8ck2ze"), )
    jscript = soup.find_all('script')[-6].string
    data = json.loads(re.search('\{("poll":.*)\}', jscript).group(0))['poll']

    today = datetime.date.today()
    next_thursday = _next_weekday(today, 3) # 0 = Monday, 1=Tuesday, 2=Wednesday...
    next_thursday = next_thursday.strftime("%-m/%-d/%y")

    df = pd.DataFrame([list(d['preferences'])for d in data['participants']]).T
    df.index = pd.MultiIndex.from_tuples([tuple(d.split()[1:]) for d in data['optionsText']])
    df.columns = [d['name'] for d in data['participants']]
    df.replace('n', False, inplace=True)
    df.replace('y', True, inplace=True)

    volunteers = {}
    for t in ('paper', 'plot'):
        volunteers[t] = list(df.columns[df.loc[next_thursday, t]])

    return volunteers
