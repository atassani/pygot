#!/usr/bin/python

from fileReader import simple_get
from bs4 import BeautifulSoup
from torrent import Torrent
from emailSender import sendStartedEmail, sendFinishedEmail
import os, re
from configReader import readConfig
from datetime import date
import shutil
import libtorrent
import time

def main():
    config = readConfig()
    checkMondayOrQuit(config)
    if isDownloadingStarted(config):
        file = getDownloadingFile(config)
        if isDownloadingFinished(config, file):
            moveFileToFinalDestination(config, file)
            sendFinishedEmail(config, file)
            removeDownloadingLock(config)
            updateDownloadChapterInConfig(config)
            removeFromTransmission(file)
	else:
            quit()
    theTorrent = getTorrentIfAny(config)
    sendStartedEmail(config, theTorrent)
    createLockFile(config, theTorrent)
    addToTransmission(theTorrent)

def addToTransmission(torrent):
    os.system('transmission-remote --add ' + torrent.magnet)

def removeFromTransmission(file):
    os.system('ID=`transmission-remote -l | grep -F ' + file +
         ' | cut -c 1-4` && transmission-remote -t $ID -r')

def checkMondayOrQuit(config):
    if (bool(config.onlyMondays)) and date.today().weekday() != 0:
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
    eztvSearchString = (config.tvShow).replace(' ', '_').lower()
    raw_html = simple_get('https://eztv.io/search/' + eztvSearchString)
    html = BeautifulSoup(raw_html, 'html.parser')
    torrents = []
    expr = re.compile(config.tvShow + ' ' + config.episode, re.I)
    for p in html.select('tr.forum_header_border'):
        row = p.select('td')
        title = row[1].text.strip()
        magnet = row[2].find('a', 'magnet').get('href')
        if (bool(expr.match(title))):
            t = Torrent(
                config.episode,
                title,
                row[3].text,
                magnet,
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
    filename = getFilenameFromMagnet(theTorrent.magnet)
    theTorrent.setFile(filename)

    return theTorrent

def getFilenameFromMagnet(magnet):
    session = libtorrent.session()
    session.listen_on(6881, 6891)
    params = {
           'save_path': '/home/osmc/tmp',
           'storage_mode': libtorrent.storage_mode_t(2),
           'paused': False,
           'auto_managed': True,
           'duplicate_is_error': True }
    handle = libtorrent.add_magnet_uri(session, magnet, params)
    session.start_dht()
    while not handle.has_metadata():
        time.sleep(1)
    torrentInfo = handle.get_torrent_info()
    #for x in range(torinfo.files().num_files()):
    return torrentInfo.files().file_path(0)

def createLockFile(config, theTorrent):
    with open(config.fileLock, 'a') as file:
        file.write(theTorrent.file)

if __name__ == "__main__":
   main()
