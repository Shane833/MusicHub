# This module will be responsible for storing the music files and providing them to 
# the player when needed such that it can play those required sounds

# Adding the given files to the path

# Custom doubly linked list
from List import List

class PlayList:
    
    # Constructor
    def __init__(self,name):
        # Name of the playlist
        self.name = name
        # Photo Cover of the playlists
        self.cover = None
        # List of songs to be played 
        self.songs = List()
        # Current song 
        self.current = None
    
    # Function to add songs to the playlist
    # Check if the song already exists then display a prompt to the user
    def add(self,song):
        # Adding the song to the playlist
        # If there is no current song set then simply make the newly added
        # song as the current song 
        if self.current is None:
            self.current = song
        # Adding the song into the list
        # as (key : Title, Value : Song Object)
        self.songs.append(song.getTitle(),song)
        # Also we will define which playlist the song belongs to
        self.songs.search(song.getTitle()).value.setPlayList(self.name)
        
    # Function to remove the song from the playlist
    def remove(self,title):
        # In order to remove the song you must supply the key i.e. the title
        self.songs.remove(title)
    
    # Function to get the desired song object as per the key
    def search(self,title):
        return self.songs.search(title)
    
    # Function to check if the playlist is empty or not
    def isEmpty(self):
        return self.songs.isEmpty()
        