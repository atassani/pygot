from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import os
import re

episode = 's08e01'
tvShow = 'game of thrones'
fileLock = '/home/osmc/downloading_got'

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

class Torrent:
    def __parseSize(self, size):
        units = {"B": 1, "KB": 10**3, "MB": 10**6, "GB": 10**9, "TB": 10**12}
        number, unit = [string.strip() for string in size.split()]
        return int(float(number)*units[unit])
    def __init__(self, title, size, magnet, link, age, seeds, sortKey):
        self.title = title
        self.size = size
        self.magnet = magnet
        self.link = link
        self.age = age
        self.seeds = seeds
        self.size_in_bytes = self.__parseSize(size)
        self.sortKey = sortKey
    def __str__(self):
        return self.title + ' '+ self.size + ' ' + str(self.seeds)
    def __eq__(self, other):
        if self.sortKey == 'seeds':
            return self.seeds == other.seeds
        else:
            return self.size_in_bytes == other.size_in_bytes
    def __lt__(self, other):
        if self.sortKey == 'seeds':
            return self.seeds < other.seeds
        else:
            return self.size_in_bytes < other.size_in_bytes

# Check if already downloading
exists = os.path.isfile(fileLock)
if exists:
    quit()

eztvSearchString = (tvShow + ' ' + episode).replace(' ', '_').lower()
raw_html = simple_get('https://eztv.io/search/' + eztvSearchString)
html = BeautifulSoup(raw_html, 'html.parser')
torrents = []
expr = re.compile(tvShow + ' ' + episode, re.I)
for p in html.select('tr.forum_header_border'):
    row = p.select('td')
    title = row[1].text.strip()
    if (bool(expr.match(title))):
        t = Torrent(
            title,
            row[3].text,
            row[2].find('a', 'magnet').get('href'),
            row[2].find('a', 'download_1').get('href'),
            row[4].text,
            int(row[5].text.replace(',', '')),
            'seeds'
            )
        torrents.append(t)

if len(torrents) == 0:
    quit()

sortedTorrents = sorted(torrents, reverse=True)

#print('\n'.join(map(str, sortedTorrents)))

# Create empty file to avoid relaunch
open(fileLock, 'a').close()

os.system('transmission-remote --add ' + sortedTorrents[0].magnet)
