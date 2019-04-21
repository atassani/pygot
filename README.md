# pygot


export EDITOR=vi
crontab -e

*/5 * * * * EMAIL_PASSWORD=email_password SENDER_EMAIL=sender_email SENDER_PASSWORD=sender_password /usr/bin/python /home/osmc/pygot/scrap.py

sudo journalctl -r
