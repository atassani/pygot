import sys
import getopt
import yaml

class Config:
    def __init__(self, configFile, fileLock, downloadedFolder, destinationFolder, episode, tvShow,
                    sender_email, email_password, receiver_email):
        self.configFile         = configFile
        self.fileLock           = fileLock
        self.downloadedFolder   = downloadedFolder
        self.destinationFolder  = destinationFolder
        self.episode            = episode
        self.tvShow             = tvShow
        self.sender_email       = sender_email
        self.email_password     = email_password
        self.receiver_email     = receiver_email

    def incEpisode(self):
        self.episode = self.episode[:-2] + format(int(self.episode[-2:])+1, '02')

    def write(self):
        yamlContent = {
            'global': {
                'destinationFolder': self.destinationFolder,
                'downloadedFolder': self.downloadedFolder,
                'fileLock': self.fileLock
            },
            'torrent': {
                'episode': self.episode,
                'tvShow': self.tvShow
            },
            'email': {
                'email_password': self.email_password,
                'receiver_email': self.receiver_email,
                'sender_email': self.sender_email
            }
        }
        with open(self.configFile, 'w') as file:
            yaml.dump(yamlContent, file, default_flow_style=False)


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
        elif opt in ("-c", "--config"):
            configFile = arg
    if configFile == '':
        usage()
        sys.exit(2)

    stream = open(configFile, 'r')
    configYaml = yaml.load(stream, Loader=yaml.SafeLoader)

    return Config(
        configFile,
        configYaml.get('global').get('fileLock'),
        configYaml.get('global').get('downloadedFolder'),
        configYaml.get('global').get('destinationFolder'),
        configYaml.get('torrent').get('episode'),
        configYaml.get('torrent').get('tvShow'),
        configYaml.get('email').get('sender_email'),
        configYaml.get('email').get('email_password'),
        configYaml.get('email').get('receiver_email')
    );

def usage():
    print 'Usage: scrap.py -c <configFile>'
