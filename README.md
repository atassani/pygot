# pygot

Allows to program the download torrents of episodes from **eztv**.
Meant to be run a a script in a raspbian, a Linux Debian distribution for Rapberry Pi ([raspbmc](https://osmc.tv/)). It is configured to be run by `cron` every 5 minutes and torrents started with `transmission`.

An email is sent when the episode appears in **eztv** and the magnet link is sent to transmission. A lock file is created to avoid re-running the process.

Working in Python 2.7.

## Usage

Make the script `scrap.py` executable in python changing the mode:

    chmod u+x scrap.py

Edit the crontab file using `vi` with this command:

      EDITOR=vi crontab -e

Introduce the following crontab configuration so that the script runs every 5 minutes.

      */5 * * * * /home/osmc/pygot/scrap.py -c /home/osmc/pygot/config.yaml >/dev/null 2>&1

To check the log of cron executions, use this command.

      sudo journalctl -r

## configuration
Create a configuration file that will be passed as a parameter to `scrap.py` with the following content:
* **fileLock**: File that will be generate when the download is started
* **episode**: Name of the episode to be downloaded. Has to be changed every time.
* **tvShow**: Name of the show to download.
* **sender_email**: The gmail user to be used to send the notifications email
* **email_password**: The password of the gmail user to be used to send the notification email.
* **receiver_email**: The gmail user that will receive the notifications.

Example:
```
email:
  email_password: Apassword
  sender_email: my@gmail.com
  receiver_email: to@gmail.com
global:
  fileLock: /home/osmc/downloading_got
  downloadedFolder: /home/osmc/download
  destinationFolder: /home/osmc/TV Shows/Game of Thrones/Season 8
torrent:
  episode: s08e01
  tvShow: game of thrones
```

## Notes
Requirements, using `pip`, have not been updated just got from

    pip freeze > requirements.txt

Dependencies

    sudo apt-get install python-libtorrent

The configuration of Transmission (torrent client) is in

    ~/.config/transmission-daemon/settings.json

It can be reloaded with
    killall -HUP transmission-daemon

Dependencies from dependabot updated, but not tested, as it is not in use anymore.
