# This module will be responsible for extracting the metadata from the 
# song like title of the song, artist's name, album name, cover art etc

# importing required modules
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE
from pathlib import Path

class Extractor:
    
    # Constructor
    def __init__(self):
        # We will pass the song object to it so that it can get all the data
        # and possibly update all of that data too
        self.song = None
        # Variable to store the metadata
        self.metadata = {'title': None,
                         'artist': None,
                         'album': None,
                         'duration': None,
                         'image': None
                        }
                        
    # Function to load the song
    def loadSong(self,song):
        self.song = song
        # Calling these functions directly after loading the song
        self.getData()
        self.setData()
    
    # Function to check if the image exists in the file
    # Returns true if the image exists else returns false
    def checkImage(self):
        # Checking for mp3 files
        if self.song.getFormat() == 'mp3':
            try:
                audio = mutagen.File(self.song.getFile())
                if audio.tags:
                    for tag in audio.tags.values():
                        if hasattr(tag, 'type') and tag.type == 3:  # Check if tag is an image
                            return True
            except Exception as e:
                print(f"Error: {e}")
            return False
        # Checking for flac files
        elif self.song.getFormat() == 'flac':
            try:
                audio = FLAC(self.song.getFile())
                if audio.pictures:
                    return True
            except Exception as e:
                print(f"Error: {e}")
            return False
        
        return False # If
            
    # Function to write that image to the disk if it exists
    def getImage(self):
        # Checking for the type of file
        if self.song.getFormat() == 'mp3':
            audio = MP3(self.song.getFile(), ID3=ID3)
            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    with open(str("Images/") + str(self.metadata['title']) + '.jpg', 'wb') as img:
                        img.write(tag.data)
                    
            return str("Images/") + str(self.metadata['title']) + ".jpg" 
        
        elif self.song.getFormat() == 'flac':
            audio = FLAC(self.song.getFile())
            image_data = None # variable to store the image data
            for pic in audio.pictures:
                image_data = pic.data
            with open(str("Images/") + str(self.metadata['title']) + '.jpg','wb') as img:
                img.write(image_data)
            
            return str("Images/") + str(self.metadata['title']) + ".jpg"
            
    # Function to retrieve all of the data
    def getData(self):
        # Retrieving the data from the song file
        if self.song.getFormat() == "mp3":
            audio = MP3(self.song.getFile(),ID3 = EasyID3)
            try:
                self.metadata['title'] = audio.get('title')[0]
                self.metadata['artist'] = audio.get('artist')[0]
                self.metadata['album'] = audio.get('album')[0]
            except TypeError: # Using this to catch None Type Error
                self.metadata['title'] = audio.get('title')
                self.metadata['artist'] = audio.get('artist')
                self.metadata['album'] = audio.get('album')
                
            self.metadata['duration'] = audio.info.length
            
            
        elif self.song.getFormat() == "wav":
            audio = WAVE(self.song.getFile())
            self.metadata['duration'] = audio.info.length
            
        elif self.song.getFormat() == "ogg":
            audio = OggVorbis(self.song.getFile())
            try:
                self.metadata['title'] = audio.get('title')[0]
                self.metadata['artist'] = audio.get('artist')[0]
                self.metadata['album'] = audio.get('album')
            except TypeError:
                self.metadata['title'] = audio.get('title')
                self.metadata['artist'] = audio.get('artist')
                self.metadata['album'] = audio.get('album')
                
            self.metadata['duration'] = audio.info.length
            
        elif self.song.getFormat() == "flac":
            audio = FLAC(self.song.getFile())
            try:
                self.metadata['title'] = audio.get('title')[0]
                self.metadata['artist'] = audio.get('artist')[0]
                self.metadata['album'] = audio.get('album')[0]
            except TypeError:
                self.metadata['title'] = audio.get('title')
                self.metadata['artist'] = audio.get('artist')
                self.metadata['album'] = audio.get('album')
                
            self.metadata['duration'] = audio.info.length

        
    # Function to display that data
    def setData(self):
        # Checking if the title of the song is None
        # If so then we can simply put it as the name of the file
        if self.metadata['title'] == None or self.metadata['title'] == "":
            self.metadata['title'] = Path(self.song.getFile()).stem 
        
        # Now checking if the image file exists
        if(self.checkImage()):
            self.metadata['image'] = self.getImage()
        else:
            self.metadata['image'] = None # Fixes the bug when there is no image present but still shows
            # that the image exists as it reads the previous values
        
        # Set this data in the song
        self.song.setTitle(self.metadata['title'])
        self.song.setArtist(self.metadata['artist'])
        self.song.setAlbum(self.metadata['album'])
        self.song.setDuration(self.metadata['duration'])
        self.song.setCover(self.metadata['image'])
        
    
    # Function to get the song object back
    def getSong(self):
        return self.song
        