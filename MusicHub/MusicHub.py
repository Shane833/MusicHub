from MusicPlayer import MusicPlayer
from MusicPlayerUI import MusicPlayerUI,VisibleSong
from List import List
from PyQt5.QtWidgets import QApplication,QFileDialog,QMessageBox,QFrame
from PyQt5.QtGui import QIcon,QPixmap
from PyQt5.QtCore import QSize, QTimer, QThread
from pathlib import Path
import os
import sys
import resources_rc # for using compiled resoruces binary

# In this file we will connect the Player and UI part together

# Ok so we would need to create another class called visible playlist which would maintain
# the same instances of the music playlist

class MusicHub(MusicPlayerUI): # Inheriting the UI element
    # Constructor
    def __init__(self): 
        super().__init__() # Calling the parent of the constructor to initalize it

        # Creating certain required variables
        self.music_player = MusicPlayer() # Handles the playing of the music
        # Another variable will be the list of Visible Songs object to be displayed
        # in the scroll area
        self.visible_songs_list = List()
        
        # Timer object for updating the seek bar
        self.seek_timer = QTimer()
        self.seek_timer.timeout.connect(self.updateSeekBar)
        # Function to setup certain functionalities for the buttons and other elements
        self.setupFunctions()
        
        # Setting the window title
        self.setWindowTitle("MusicHub")
        self.setStyleSheet("color : rgba(#FFFFF7);")
        self.show()
        
    # Function to initialize various functionalities
    def setupFunctions(self):
        # Setting the value of the volume slider to be 100 at start
        self.vol_slider.setValue(100)
    
        # Connecting the specific buttons to their respective signals
        self.add_song_but.clicked.connect(self.addSong) # Add Song functionality
        self.play_but.clicked.connect(self.pauseResumeSong) # Pause Resume functionality
        self.vol_slider.sliderMoved.connect(self.changeVolume) # Change Volume Functionality
        self.min_vol_but.clicked.connect(self.muteVolume) # Mute Volume Functionality
        self.clear_song_but.clicked.connect(self.clearScrollArea) # Function to clear all the songs
        self.repeat_but.clicked.connect(self.repeat) # Repeat Functionality
        self.shuffle_but.clicked.connect(self.shuffle)
        # ****
        # Lets leave it for now faulty behaviour, either some other song starts playing etc
        #self.time_slider.sliderReleased.connect(self.changeSongPosition)
        # ****
        self.next_but.clicked.connect(self.nextSong)
        self.prev_but.clicked.connect(self.prevSong)
        self.add_folder_but.clicked.connect(self.addSongFolder)
        
        # Connecting the end event handling
        # self.music_player.player.sound_finished.connect(self.handleEndEvent)
        
        
    def addSong(self,files = None):
        # If we provide the addtional files
        if files:
            self.music_player.addSongs(files)
        else:
            # Opening the file dialog box to let the user select the songs
            filenames,_ = QFileDialog.getOpenFileNames(self,"Load Songs","","mp3 files (*.mp3);;wav files (*.wav);;ogg files(*.ogg);; All files (*.mp3 *.wav *.flac *.ogg)")
            # Adding those songs into the MusicPlayer's MusicPlayList
            self.music_player.addSongs(filenames)
            
        # Now again I also want to add the selected songs in the scroll area
        # But first they must be appended in the visible song list
        for i in self.music_player.playing_queue.songs_copy.getKeys():
            if i not in self.visible_songs_list.getKeys(): # This condition also takes care of redundant values
                # First we will create the widget and connect them with their specific signal
                widget = VisibleSong(i)
                # Connectint that widget to a method
                widget.play_song_but.clicked.connect(lambda _,w=widget:self.playSongFromScroll(w.title))
                self.songs_box.addWidget(widget)
                separator = QFrame(self)
                separator.setFrameShape(QFrame.HLine)  # Horizontal line separator
                separator.setFrameShadow(QFrame.Sunken)
                self.songs_box.addWidget(separator)
                # Now adding it to the list
                self.visible_songs_list.append(i,widget)
        
    def playSong(self,seekBarValue = None):
        # While playing the song we must handle updating somethings
        # 1. Initializing the seekbar and set the end duration
        # 2. Calling the music player to play the songs
        # 3. Updating the seekbar periodically
        
        # 1. Retrieving the length of the song
        # It returns the song length in seconds
        song_length = int(self.music_player.playing_queue.current.getDuration())
        self.time_slider.setValue(0)
        self.time_slider.setRange(0,song_length)
        self.end_time.setText(" " + self.seconds_to_mm_ss(song_length))
        # 2. Playing the song
        self.music_player.playSong()
        
        # Also whenever this function is called we must change the icon on the play/pause button
        self.play_but.setIcon(QIcon(":Assets/pause.png"))
        self.play_but.setIconSize(QSize(63,63))
        self.play_but.setStyleSheet("background-color : none")
        self.play_but.resize(QSize(63,63))
        
        self.seek_timer.stop()
        # 3. Repeatedly updating the seek bar
        self.seek_timer = QTimer(self)
        self.seek_timer.timeout.connect(lambda : self.updateSeekBar(seekBarValue))
        self.seek_timer.start(1000)
        
    
    # Function to play the next song in the list
    def nextSong(self):
        # Follow these steps
        # call the helper function
        # Update the image and scroll area
        # again call the play function
        
        # 1. Calling the helper function
        next_song_key = self.music_player.playNextSong()
        
        
        if next_song_key != None:
            # 2. update the image and scroll area
            self.updateScrollArea(next_song_key)
            self.updateImageArea()
            # 3. Playing the song
            self.playSong()
            
    # Function to play the previous song in the list
    def prevSong(self):
        # Obtaining the previous song from the helper function
        prev_song_key = self.music_player.playPreviousSong()
        
        if prev_song_key != None:
            # Update
            self.updateScrollArea(prev_song_key)
            self.updateImageArea()
            # Play
            self.playSong()
            

    def playSongFromScroll(self,title):
        # Whenever we would play the song from the scroll area
        # There are certain things that must be done
        # 0. But first you must change the attributes of the already current element
        # 1. Identify which song element has called that signal
        # 2. Get the corresponding key and set that song to be the current 
        # 3. Update the texts and images accordingly
        # 4. Play the song
        # Better to divide these functionalities into different functions
        
        # 1. Updating the scroll area and setting current song
        self.updateScrollArea(title)
        # 2. Update the texts and iamges on the first page
        self.updateImageArea()
        # 4. Playing the song
        self.playSong()
    
    # Function to update the element in the scroll area
    def updateScrollArea(self,title):
        # Get the current song key and then update its color
        current_song_key = self.music_player.playing_queue.current.getTitle()
        # Now we have to set this current label color to be black instead of red
        current_widget_label = self.visible_songs_list.search(current_song_key).value.visible_title
        current_widget_button = self.visible_songs_list.search(current_song_key).value.play_song_but
        current_widget_label.setStyleSheet("color : black;")
        current_widget_button.setIcon(QIcon(":Assets/small-play.png"))
        current_widget_button.setIconSize(QSize(20,20))
        current_widget_button.setStyleSheet("background-color : none")
        current_widget_button.resize(QSize(20,20))
        
        # Now find the new song to be played
        new_song_key = self.music_player.playing_queue.songs_copy.search(title).key
        new_widget_label = self.visible_songs_list.search(new_song_key).value.visible_title
        new_widget_button = self.visible_songs_list.search(new_song_key).value.play_song_but
        new_widget_label.setStyleSheet("color : red;")
        new_widget_button.setIcon(QIcon(":Assets/playing.png"))
        new_widget_button.setIconSize(QSize(20,20))
        new_widget_button.setStyleSheet("background-color : none")
        new_widget_button.resize(QSize(20,20))
        
        # Now you would also need to update to be current song
        current_song = self.music_player.playing_queue.songs.search(title).value
        self.music_player.playing_queue.current = current_song
    
    # Utitlity function for stopping the playback and clearing lists
    def clearLists(self):
        # First clearing all the lists
        self.visible_songs_list.clear()
        self.music_player.playing_queue.songs.clear()
        self.music_player.playing_queue.songs_copy.clear()
    
    # Utility function to keep back the values to a default
    def setDefault(self):
        # Also set current song to be none
        self.music_player.playing_queue.current = None
        # Now I also want to stop any of the currently playing music
        # and clear all the details associated with it 
        self.music_player.player.stop()
        
        self.time_slider.setValue(0)
        self.current_time.setText("00:00")
        self.end_time.setText(" 00:00")
        # Defaulting the icon
        self.play_but.setIcon(QIcon(":Assets/play-button.png"))
        self.play_but.setIconSize(QSize(60,60))
        self.play_but.setStyleSheet("background-color : none")
        self.play_but.resize(QSize(60,60))
        # Defaulting the labels
        self.song_name.setText("Unknown    ")
        self.artist_name.setText("Unknown")
        
        pixmap = QPixmap(":Assets/musical.png")
        pixmap = pixmap.scaled(500,500)
        self.image_label.setPixmap(pixmap)
        
    # Utility function to clear the widgets in the scroll area
    def clearWidgets(self):
        # First we check the count and loop through it
        while self.songs_box.count():
            item = self.songs_box.takeAt(0) # Obtain the item at first place
            widget = item.widget() # Obtain the widget from the item if any exists
            if widget:
                widget.deleteLater() # Then we simply schedule it for being deleted
        
    # Function to clear the scroll area when the button is pressed
    def clearScrollArea(self):
        self.clearWidgets()
        # Now one more things to do is to clear the current playing song
        # and the corresponding list
        self.clearLists()
        # Defaulting other components
        self.setDefault()
    
    # Function to update the elements in the image page plus the song info
    def updateImageArea(self):
        # Get the song title, artist and image location from the current song
        title = self.music_player.playing_queue.current.getTitle()
        artist = self.music_player.playing_queue.current.getArtist()
        image = self.music_player.playing_queue.current.getCover()
        
        self.song_name.setText(title + "    ")
        
        # Now we will check the conditions if any of the data is null
        if artist is None:
            self.artist_name.setText("Unknown")
        else:
            self.artist_name.setText(artist)
        
        # Now we will check if the image exists or not
        if image is None:
            pixmap = QPixmap(":Assets/musical.png")
            pixmap = pixmap.scaled(500,500)
            self.image_label.setPixmap(pixmap)
        else:
            pixmap = QPixmap(image)
            pixmap = pixmap.scaled(500,500)
            self.image_label.setPixmap(pixmap)
            
        
    # Function to update the seek bar
    def updateSeekBar(self,value = None):
        current_value = self.music_player.player.getElapsedTime() # time in milli seconds
        current_value = int(current_value / 1000)
        if value != None and value != 0:
            current_value = current_value + value
        self.time_slider.setValue(current_value)
        # Along with the seekbar we can also update our current time label
        self.current_time.setText(self.seconds_to_mm_ss(current_value))
        # Now one more condition we can check if the song has finished 
        # we can simple drop that additional value
            
    
    # Function to convert the seconds to the format mm:ss
    def seconds_to_mm_ss(self,seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def pauseResumeSong(self):        
        # Calling our pasueResume function
        self.music_player.pauseResumeSong()

        if self.music_player.player.isPlaying():
            if not self.music_player.player.PAUSED:
                self.play_but.setIcon(QIcon(":Assets/pause.png"))
                self.play_but.setIconSize(QSize(63,63))
                self.play_but.setStyleSheet("background-color : none")
                self.play_but.resize(QSize(63,63))
  
        elif not self.music_player.player.isPlaying():
            if self.music_player.player.PAUSED:
                self.play_but.setIcon(QIcon(":Assets/play-button.png"))
                self.play_but.setIconSize(QSize(60,60))
                self.play_but.setStyleSheet("background-color : none")
                self.play_but.resize(QSize(60,60))  

    # Function to change the volume of the song as per the user
    def changeVolume(self,value):
        # Here we will simply change the volume as per the value
        # Since our player only takes volume in 0.0 to 1.0
        # so we would have to change that
        new_vol = value / 100
        self.music_player.player.setVolume(new_vol)
    
    # Function to mute the volume 
    def muteVolume(self):
        # Check if its already mute or not
        # if yes then set volume to be zero and change the icons
        if self.music_player.player.MUTE:
            # Setting the current flag value
            self.music_player.player.MUTE = False
            # Setting the volume as per the slider
            self.changeVolume(self.vol_slider.value())
            # now change the icon
            self.min_vol_but.setIcon(QIcon(":Assets/sound.png"))
            self.min_vol_but.setIconSize(QSize(20,20))
            self.min_vol_but.setStyleSheet("background-color : none")
            self.min_vol_but.resize(QSize(20,20))
            
        else:
            # Setting the correct flag value
            self.music_player.player.MUTE = True
            # Now set the volume to be 0
            self.changeVolume(0)
            # now change the icon on the button
            self.min_vol_but.setIcon(QIcon(":Assets/mute.png"))
            self.min_vol_but.setIconSize(QSize(20,20))
            self.min_vol_but.setStyleSheet("background-color : none")
            self.min_vol_but.resize(QSize(20,20))
        
    # Function to change the position of the song as per the user
    def changeSongPosition(self):
        # Ok so as per pygame.mixer doc
        # Changing song position is only implemented for 2 format
        # However you must check if the song is playing or not
        # 1. OGG : absolute position in seconds from the start is accepted
        # 2. MP3 : accepts the relative position in seconds from current position
        # for implementing absolute positioning use rewind() then position
        
        # Store the current time slider value
        current_position = self.time_slider.value()
        # Check if the format of the current song
        if self.music_player.player.isPlaying():
            if self.music_player.playing_queue.current.getFormat() == 'mp3':
                self.music_player.player.stop()
                self.music_player.player.rewind()
                #self.seek_timer.disconnect() # Disconnect the timer else 2 separate threads run
                self.playSong(current_position) 
                self.music_player.player.setPlaybackTime(current_position) # Play the song
                self.time_slider.setValue(current_position)
                self.current_time.setText(self.seconds_to_mm_ss(current_position))
                # Now this works but the problem is that:
                # When the seekbar is updated it gets updated from the elapsedtime function
                # However that elapsed time is the total elapsed time that has passed since the
                # beginning of the player, it don't take it into account
                # Hence you would have to update the song accordingly
    
    def addSongFolder(self):
        # First open the folder dialog and 
        folder = QFileDialog.getExistingDirectory(self,"Select Directory")
        
        # Now if any folder is selected then,
        # We search through them and find the required files
        if folder:
            directory = Path(folder)
            files = []
            for item in directory.glob("*.mp3"):
                files.append(str(item)) # Converting to string bcz it returns a path object
            for item in directory.glob("*.wav"):
                files.append(str(item))
            for item in directory.glob("*.ogg"):
                files.append(str(item))
            for item in directory.glob("*.flac"):   
                files.append(str(item))
                
            # add the songs using the custom function and provide this list as the argument
            self.addSong(files)

    # Function to handle the end event or when the song finishes
    def handleEndEvent(self):
        self.music_player.handleEndEvent()
    
    # Function for handling repeat Functionality
    def repeat(self):
        # first call the repeat helper function
        self.music_player.toggleRepeat()
        # Here based on the flags we will change the icons
        if self.music_player.playing_queue.REPEAT:
            self.repeat_but.setIcon(QIcon(":Assets/repeat.png"))
            self.repeat_but.setIconSize(QSize(30,30))
            self.repeat_but.setStyleSheet("background-color : none")
            self.repeat_but.resize(QSize(30,30))
        
        elif self.music_player.playing_queue.REPEATONCE:
            self.repeat_but.setIcon(QIcon(":Assets/repeat-once.png"))
            self.repeat_but.setIconSize(QSize(32,32))
            self.repeat_but.setStyleSheet("background-color : none")
            self.repeat_but.resize(QSize(32,32))
            
        else:
            self.repeat_but.setIcon(QIcon(":Assets/repeat-default.png"))
            self.repeat_but.setIconSize(QSize(30,30))
            self.repeat_but.setStyleSheet("background-color : none")
            self.repeat_but.resize(QSize(30,30))
    
    # Function to handling shuffle functionality
    def shuffle(self):
        # First call the helper function
        self.music_player.toggleShuffle()
        
        # The change the icon depending on the flag value
        if self.music_player.playing_queue.SHUFFLE is True:
            self.shuffle_but.setIcon(QIcon(":Assets/shuffle.png"))
            self.shuffle_but.setIconSize(QSize(35,35))
            self.shuffle_but.setStyleSheet("background-color : none")
            self.shuffle_but.resize(QSize(35,35))
        else:
            self.shuffle_but.setIcon(QIcon(":Assets/shuffle-default.png"))
            self.shuffle_but.setIconSize(QSize(35,35))
            self.shuffle_but.setStyleSheet("background-color : none")
            self.shuffle_but.resize(QSize(35,35))
        
        # Now we must update the scroll area
        self.clearWidgets()
        # plus clear the visible songs list
        self.visible_songs_list.clear()
        # Now add the visible songs list again
        for i in self.music_player.playing_queue.songs_copy.getKeys():
            if i not in self.visible_songs_list.getKeys(): # This condition also takes care of redundant values
                # First we will create the widget and connect them with their specific signal
                widget = VisibleSong(i)
                # Connectint that widget to a method
                widget.play_song_but.clicked.connect(lambda _,w=widget:self.playSongFromScroll(w.title))
                self.songs_box.addWidget(widget)
                separator = QFrame(self)
                separator.setFrameShape(QFrame.HLine)  # Horizontal line separator
                separator.setFrameShadow(QFrame.Sunken)
                self.songs_box.addWidget(separator)
                # Now adding it to the list
                self.visible_songs_list.append(i,widget)
        
        # Now identify the current playing song and paint it red
        # But first check if there is something in the list or not
        if self.music_player.playing_queue.songs.isEmpty() is False:
            current_song_key = self.music_player.playing_queue.current.getTitle()
            # Now we have to set this current label color to be black instead of red
            current_widget_label = self.visible_songs_list.search(current_song_key).value.visible_title
            current_widget_button = self.visible_songs_list.search(current_song_key).value.play_song_but
            current_widget_label.setStyleSheet("color : red;")
            current_widget_button.setIcon(QIcon(":Assets/playing.png"))
            current_widget_button.setIconSize(QSize(20,20))
            current_widget_button.setStyleSheet("background-color : none")
            current_widget_button.resize(QSize(20,20))  
    
    # Function to connect

def main():
    app = QApplication(sys.argv)
    window = MusicHub()
    sys.exit(app.exec_())

# Calling the main Function
if __name__ == "__main__":
    main()
    
