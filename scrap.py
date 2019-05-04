#!/usr/bin/python

from fileReader import simple_get
from bs4 import BeautifulSoup
from torrent import Torrent
from emailSender import sendStartedEmail, sendFinishedEmail
import os, re
from configReader import readConfig
from datetime import date
import shutil

def main():
    config = readConfig()
    checkMondayOrQuit()
    if isDownloadingStarted(config):
        file = getDownloadingFile(config)
        if isDownloadingFinished(config, file):
            moveFileToFinalDestination(config, file)
            sendFinishedEmail(config, file)
            removeDownloadingLock(config)
            updateDownloadChapterInConfig(config)
            removeFromTransmission(file)
        quit()
    theTorrent = getTorrentIfAny(config)
    sendStartedEmail(config, theTorrent)
    createLockFile(config, theTorrent)
    addToTransmission(theTorrent)

def addToTransmission(torrent):
    os.system('transmission-remote --add ' + torrent.magnet)

def removeFromTransmission(file):
    os.system('ID=`transmission-remote -l | grep -F ' + file
        + ' | cut -c 1-4` && transmission-remote -t $ID -r')

def checkMondayOrQuit():
    if date.today().weekday() != 0:
        quit()

def isDownloadingStarted(config):
    exists = os.path.isfile(config.fileLock)
    return exists

def getDownloadingFile(config):
    with open(config.fileLock, 'r') as f:
        data = f.read()
        return data

def isDownloadingFinished(config, file):
    return os.path.isfile(config.downloadedFolder + '/' + file)

def moveFileToFinalDestination(config, file):
    shutil.move(os.path.join(config.downloadedFolder, file), os.path.join(config.destinationFolder, file))

def removeDownloadingLock(config):
    os.remove(config.fileLock)

def updateDownloadChapterInConfig(config):
    config.incEpisode()
    config.write()

def getTorrentIfAny(config):
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

    #print('\n'.join(map(str, sortedTorrents)))

    return theTorrent

def createLockFile(config, theTorrent):
    with open(config.fileLock, 'a') as file:
        file.write(theTorrent.file)

if __name__ == "__main__":
   main()
