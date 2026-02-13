# This module will represent a song as an entity and would comprise of 
# the details associated with the song like name, artist, album, cover art etc

class Song:
    # Constructor
    def __init__(self):
        # Song attributes
        self.title = None # Title of the Song
        self.artist = None # Artists' name
        self.album = None # Album's name
        self.duration = None # Length of the song
        self.location = None # File location of the song
        self.cover = None # Album cover art of the song
        self.playing = None # Boolean value defines if the song is currently 
                            # playing or not
        self.format = None # Defines the format of the song
        self.playlist = None # Defines which playlist the song belongs to
    
    # String Equivalent of the function
    def __str__(self):
        return f'Title : {self.title}\nArtist : {self.artist}\nAlbum : {self.album}\nPlayList : {self.playlist}\nCover : {self.cover}\nDuration : {self.duration}\nFormat : {self.format}\n'
    
    # Utility functions
    
    # SETTER FUNCTIONS
    def setTitle(self,title):
        self.title = title
    
    def setArtist(self,artist):
        self.artist = artist
    
    def setAlbum(self,album):
        self.album = album
    
    def setDuration(self,duration):
        self.duration = duration
    
    def setPlaying(self,state):
        self.playing = state
    
    def setFormat(self,format):
        self.format = format
    
    def setCover(self,cover):
        self.cover = cover
    
    def setPlayList(self,playlist):
        self.playlist = playlist
    
    # Function to load the song location
    def setFile(self,filename):
        # Setting the file location
        self.location = filename
        
        # Extracting the format from the file
        if filename.endswith(".mp3"):
            self.setFormat("mp3")
        elif filename.endswith(".wav"):
            self.setFormat("wav")
        elif filename.endswith(".ogg"):
            self.setFormat("ogg")
        elif filename.endswith(".flac"):
            self.setFormat("flac")
    
    # GETTER FUNCTIONS
    def getTitle(self):
        return self.title
    
    def getArtist(self):
        return self.artist
    
    def getAlbum(self):
        return self.album
    
    def getDuration(self):
        return self.duration
    
    def getPlaying(self):
        return self.playing
    
    def getFormat(self):
        return self.format
    
    def getFile(self):
        return self.location
    
    def getCover(self):
        return self.cover
    
    def getPlayList(self):
        return self.playlist
    
    
        