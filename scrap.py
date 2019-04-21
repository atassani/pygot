#!/usr/bin/python

from fileReader import simple_get
from bs4 import BeautifulSoup
from torrent import Torrent
from emailSender import sendEmail
from yaml import load, FullLoader
import os, re
import sys
import getopt
from configReader import readConfig

def main():
    config = readConfig()

    # Check if already downloading
    exists = os.path.isfile(config.fileLock)
    if exists:
        quit()

    eztvSearchString = (config.tvShow + ' ' + config.episode).replace(' ', '_').lower()
    raw_html = simple_get('https://eztv.io/search/' + eztvSearchString)
    html = BeautifulSoup(raw_html, 'html.parser')
    torrents = []
    expr = re.compile(config.tvShow + ' ' + config.episode, re.I)
    for p in html.select('tr.forum_header_border'):
        row = p.select('td')
        title = row[1].text.strip()
        if (bool(expr.match(title))):
            t = Torrent(
                config.episode,
                title,
                row[3].text,
                row[2].find('a', 'magnet').get('href'),
                row[2].find('a', 'download_1').get('href'),
                row[4].text,
                int(row[5].text.replace(',', ''))
                )
            torrents.append(t)

    if len(torrents) == 0:
        quit()

    # The file with more seeds that is bigger that 1Gb
    torrentsBigger1G = [t for t in torrents if t.size_in_bytes > 1000000000]
    torrents = torrentsBigger1G

    if len(torrents) == 0:
        quit()

    sortedTorrents = sorted(torrents, reverse=True)
    theTorrent = sortedTorrents[0]

    print('\n'.join(map(str, sortedTorrents)))

    sendEmail(config, theTorrent)

    # Create empty file to avoid relaunch
    open(config.fileLock, 'a').close()

    os.system('transmission-remote --add ' + theTorrent.magnet)

if __name__ == "__main__":
   main()
