import sys
import getopt
import yaml

class Config:
    def __init__(self, fileLock, episode, tvShow, sender_email, email_password, receiver_email):
        self.fileLock       = fileLock
        self.episode        = episode
        self.tvShow         = tvShow
        self.sender_email   = sender_email
        self.email_password = email_password
        self.receiver_email = receiver_email

def readConfig():
    configFile = ''
    if len(sys.argv) < 2:
        usage()
        sys.exit(2)
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hc:', ['config='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-c", "--ifile"):
            configFile = arg
    if configFile == '':
        usage()
        sys.exit(2)

    stream = open(configFile, 'r')
    configYaml = yaml.load(stream, Loader=yaml.FullLoader)

    return Config(
        configYaml.get('global').get('fileLock'),
        configYaml.get('torrent').get('episode'),
        configYaml.get('torrent').get('tvShow'),
        configYaml.get('email').get('sender_email'),
        configYaml.get('email').get('email_password'),
        configYaml.get('email').get('receiver_email')
    );

def usage():
    print 'Usage: scrap.py -c <configFile>'
