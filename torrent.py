class Torrent:
    def __parseSize(self, size):
        units = {"B": 1, "KB": 10**3, "MB": 10**6, "GB": 10**9, "TB": 10**12}
        number, unit = [string.strip() for string in size.split()]
        return int(float(number)*units[unit])
    def __init__(self, episode, title, size, magnet, age, seeds):
        self.episode = episode
        self.title = title
        self.size = size
        self.magnet = magnet
        self.age = age
        self.seeds = seeds
        self.size_in_bytes = self.__parseSize(size)
    def setFile(self, file):
	self.file = file
    def __str__(self):
        return self.title + ' '+ self.size + ' ' + str(self.seeds)
    def __eq__(self, other):
        return self.seeds == other.seeds
    def __lt__(self, other):
        return self.seeds < other.seeds
