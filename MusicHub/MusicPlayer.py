# This module will combine all of the other modules to use them
# It will implment its own loading, playback, playlist handler functions

from Player import Player
from Song import Song
from PlayList import PlayList
from Extractor import Extractor
from List import List
import pickle # Used for serializing and here for saving playlists to disc
import random # This module will be responsible for shuffling the songs in the playlist
# This module will be needed to concurrently handle the pygame events 
from PyQt5.QtCore import QTimer,pyqtSlot

# Creating a custom playlist class to handle certain other features such as shuffle,repeat etc
class MusicPlayList(PlayList):
    # Constructor
    def __init__(self,name):
        # Calling the super class's constructor
        super().__init__(name)
        # Defining two new attribute
        self.REPEAT = False
        self.REPEATONCE = False
        self.SHUFFLE = False
        # and defining a new list which will be responsible for operations like shuffle, sorting etc
        self.songs_copy = List()
        # The add and remove functions must be overwritten for this class
    
    def add(self,song):
        if self.current is None:
            self.current = song

        self.songs.append(song.getTitle(),song)
        # Adding the same to the new list too
        self.songs_copy.append(song.getTitle(),None)
        self.songs.search(song.getTitle()).value.setPlayList(self.name)
    
    def remove(self,title):
        # Remove the song from the new list too
        self.songs.remove(title)
        self.songs_copy.remove(title)
             
    # Introducing the new functions of shuffling and sorting the playlists
    def shuffle(self):
        # First we will check if the shuffle is on/off
        if self.SHUFFLE is False:
            # Then we set shuffle to be true
            self.SHUFFLE = True
            # In this function first we will acquire all of the keys 
            keys = self.songs_copy.getKeys()
            # clear the current existing list 
            self.songs_copy.clear()
            # shuffle them using the random module
            random.shuffle(keys)
            # Appending the same back in the list
            for k in keys:
                self.songs_copy.append(k,None)
        else:
            # and now we will simply turn it off
            self.SHUFFLE = False
            # In this case we will simply copy the orginal data back in the list
            keys = self.songs.getKeys()
            # clearing the current list
            self.songs_copy.clear()
            # Copying the data
            for k in keys:
                self.songs_copy.append(k,None)
    
    # Function to toggle repeat, repeatonce
    def repeat(self):
        # Checking for every possible solution and assigning values accordingly
        if self.REPEAT is False and self.REPEATONCE is False:
            self.REPEAT = True
        elif self.REPEAT is True and self.REPEATONCE is False:
            self.REPEATONCE = True
            self.REPEAT = False
        elif self.REPEAT is False and self.REPEATONCE is True:
            self.REPEAT = False
            self.REPEATONCE = False
        
        
class MusicPlayer:
    # Constructor
    def __init__(self):
        # Maintains its own playing queue
        # When you wish to load or create a playlist you can do so with its help
        self.playing_queue = MusicPlayList("Current Queue")
        # This is the part of the music player which actually plays the music
        self.player = Player()
        # This is the metadata extractor module 
        self.extractor = Extractor()
        # Another variable we can check is the song finished 
        self.SONG_FINISHED = False
        
    # Loading a single song
    def addSong(self,filename):
        # Loading the song into a temporary object
        self.song = Song()
        self.song.setFile(filename)
        # Extracting the data from the song
        self.extractor.loadSong(self.song)
        self.song = self.extractor.getSong()
        # Adding this object to the playlist
        self.playing_queue.add(self.song)
    
    # Loading multiple songs
    def addSongs(self,filenames):
        # Loads multiple files at once
        for f in filenames:
            self.addSong(f)
    
    # Function to play the song
    def playSong(self):
        # First checking if there exists any song in the playing queue
        if self.playing_queue.isEmpty():
            pass
        else:
            # Unloading the current resource from the player
            self.player.unload()
            # Retreiving the file from the current song in the playlist
            song_file = self.playing_queue.current.getFile()
            # Now we will toggle the playing state of the song to be true
            self.playing_queue.current.setPlaying(True)
            # Passing this file to be loaded into the player
            self.player.load(song_file)
            # Also to let the song finsihed flag false
            self.SONG_FINISHED = False
            # Now playing the song
            self.player.play()
            
            # Also reset the pause and resume flag
            self.player.PAUSED = False
            
            self.timer = QTimer()
            self.timer.timeout.connect(self.player.checkEvent)
            self.timer.start(50)
        
    # Function to pause the song
    def pauseResumeSong(self):
        # We will go through a couple of conditions first
        # before pausing the playback
        
        # First we will check if anything is being played or not
        if self.player.isPlaying():
            # Now again checking the state of the player if it is paused
            if not self.player.PAUSED:
                # Now we can pause the song
                self.player.pause()
        # Again we will check if the player is playing or not
        # and if it is not then we will resume the song else nothing happens
        elif not self.player.isPlaying():
            if self.player.PAUSED:
                # Now we can resume the song
                self.player.resume()
            
    # Function to play the next song in the list
    # MISTAKE : In the play next and play previous functions the sequence of the playing queue is referenced
    # from the original songs list instead of the copy songs list
    def playNextSong(self):
        # First make sure to check a couple of conditions
        # 1. If the list is empty then its no use to play next
        if self.playing_queue.isEmpty():
            pass
        else:
            # Now first we will search for the song that is currently playing
            current = None
            for k in self.playing_queue.songs_copy.getKeys():
                if self.playing_queue.songs.search(k).value.getPlaying() is True:
                    # CHANGE : Instead of the holding the reference of the original song
                    # we will hold the reference of the songs_copy song
                    #current = self.playing_queue.songs.search(k)
                    current = self.playing_queue.songs_copy.search(k)
                    break
            # Now we will obtain its next element and check if its None or not
            if current.next is None:
                # First we will check if the repeat option is enabled or not
                if self.playing_queue.REPEAT is True:
                    # In this case we will set the curent song to be the one at the head of the list
                    # First set its playing status to be False
                    self.playing_queue.current.setPlaying(False)
                    # Retrieving the song at the head of the list
                    new_song = self.playing_queue.songs_copy.head.key
                    # Now setting this to be the current song
                    # Commenting out the below section bcz we don't want to set the current song just now
                    # self.playing_queue.current = self.playing_queue.songs.search(new_song).value
                    # Now simply play it 
                    # self.playSong() 
                    # return True # New modification as per the integration instead of returning true or false
                    # we can directly return the key if its found
                else:
                    # pass # Simply do nothing about that
                    # return False # This will let us know if the new song is played or not
                    return None
            else:  
                # However if there is something then we will set the new current song
                self.playing_queue.current.setPlaying(False)
                # Setting the new current as the next song
                
                # CHANGES HERE FOR SHUFFLE ERROR
                # Instead of the below commented code we will derive the next song from the songs_copy list
                # self.playing_queue.current = current.next.value
                # self.playing_queue.current = self.playing_queue.songs.search(current.next.key).value
               
                # And now we can call the play function
                # self.playSong()
                
                # return True # Lets us know that the next song has been played
                return current.next.key
                
                
            
    # Function to play the previous song in the list
    # CHANGES : Making the same changes here
    def playPreviousSong(self):
        # 1. Check if the queue is empty 
        if self.playing_queue.isEmpty():
            pass
        else:
            # Now first we will search for the song that is currently playing
            current = None
            for k in self.playing_queue.songs_copy.getKeys():
                if self.playing_queue.songs.search(k).value.getPlaying() is True:
                    current = self.playing_queue.songs_copy.search(k)
                    break
            # Now we will obtain its next element and check if its None or not
            if current.prev is None:
                # If there exists no song previous to current one then we can simply rewind it
                # self.playSong()
                return current.key # New return value after integration
            else:  
                # However if there is something then we will again check one more condition
                # We will check if the elapsed time is less than 2 seconds
                # 1. If it is less than 2 seconds then we will play the previous song
                if self.player.getElapsedTime() < 2000:
                    self.playing_queue.current.setPlaying(False)
                    # Setting the new current as the next song
                    # self.playing_queue.current = self.playing_queue.songs.search(current.prev.key).value
                    # And now we can call the play function
                    # self.playSong()
                    return current.prev.key
                # 2. If its not less than 2 seconds then we can simply rewind the song
                else:
                    return current.key
                    # self.playSong()
    
    # Function to handle the event when the sound finished
    @pyqtSlot()
    def handleEndEvent(self):
        # First of all we will check for the repeat once flag
        if self.playing_queue.REPEATONCE is True:
            # In this case we can simply rewind the sound
            self.playSong()
        # Now we will check if the simple repeat is checked on
        elif self.playing_queue.REPEAT is True:
            # In this case we will set the curent song to be the one at the head of the list
            # First set its playing status to be False
            self.playing_queue.current.setPlaying(False)
            # Retrieving the song at the head of the list
            new_song = self.playing_queue.songs_copy.head.key
            # Now setting this to be the current song
            self.playing_queue.current = self.playing_queue.songs.search(new_song).value
            # Now simply play it 
            self.playSong()
           
        # In the last case we will simply play the next song
        else:
            self.SONG_FINISHED = True # This will force to update the flag even if there is no next song
            self.playNextSong()
        
        # Here once the song is finished we will set the corresponding flag
   
        
    # Function to toggle shuffle
    def toggleShuffle(self):
        # Simply call the shuffle function in the playing queue
        self.playing_queue.shuffle()
    
    # Function to toggle repeat
    def toggleRepeat(self):
        # simply call the repeat function
        self.playing_queue.repeat()
       
