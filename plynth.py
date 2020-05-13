# A super simple python program to turn your Raspberry Pi into a "record player",
# based on the technology behind Plynth (http://www.plynth.com). Uses the Google
# Vision and Spotify APIs, as well as Spotipy for album searching and Mopidy to
# play Spotify on the Pi. Thanks to Patrick Weaver for inspiration on how to
# improve the Spofity search funtionality (http://record-player.glitch.me).

# To get this running, you'll firstneed to install Mopidy and add your Google
# crecentials as environmental variables and your Spotify credentials to the
# Mopidy configuration file. More information can be found in the README file.

from gpiozero import LED, Button
from picamera import PiCamera
from subprocess import call
from time import sleep
from signal import pause
import io
import os
import re

from google.cloud import vision
from google.cloud.vision import types

from mpd import MPDClient
import spotipy

# configures the camera. Shutter speed is high to account for low lighting. Since the album is stationary, this usually isn't an issue
camera = PiCamera()
camera.resolution = (1024, 768)
camera.shutter_speed = 2000

led = LED(15)

# this keeps track of scans, if you try to scan a new album while one is in the process of being scanned
current_scan = 0

# this is the main function, which takes a photo of the album, uploads it to Google Vision and then searches Spotify


def plynth_scan():

    # stops the track that's currently playing and starts the light blinking
    MPDClient.stop()
    MPDClient.clear()
    led.blink(on_time=0.5, off_time=0.5, fade_in_time=0.5, fade_out_time=0.5)

    # Increments the scan counts and creates a 'scan id' for this scan
    global current_scan
    current_scan += 1
    scan_id = current_scan

    sleep(0.5)

    # Takes a photo
    camera.capture('photo.jpg')

    try:
        # Sends the image to Google Vision to be identified
        client = vision.ImageAnnotatorClient()
        file_name = os.path.join(os.path.dirname(__file__), 'photo.jpg')
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()
        image = types.Image(content=content)

        # Gets the response from Google Vision pulls the "best guess"
        gvresponse = client.web_detection(image=image).web_detection
        album_guess = gvresponse.bestGuessLabels[0].label

        # Removes a bunch of characters that might mess up Spotify
        regex = re.compile('[]()<>+_^%$#@,.!?]')
        album_guess = regex.sub(' ', album_guess)

        # Searches Spotify for the guess from Google Vision
        albums = spotify_search(album_guess)

        # If no albums are foumd, removes certain 'censored' words that may be tripping it up. Thanks to Patrick Weaver for this one.
        if len(albums) == 0:
            censoredWords = ['album', 'cover', 'vinyl', 'usa',
                             'import', 'lp', 'cd', 'soundtrack', 'german import']
            word_list = album_guess.split()
            album_guess = ' '.join(
                [i for i in word_list if i not in censoredWords])
            albums = spotify_search(album_guess)

        # If still no albums are found, removes the last word and retries
        while len(albums) == 0:
            album_guess = ' '.join(album_guess.split(' ')[:-1])
            if len(album_guess) == 0:
                plynth_stop()
            else:
                albums = spotify_search(album_guess)

        # Once an album is found, gets the album's uri
        album_uri = albums[0]['uri']

        # Checks to make sure there aren't any more recent scans, then plays the album
        if scan_id == current_scan:
            MPDClient.add(album_uri)
            MPDClient.next()
        else:
            plynth_stop()
    except Exception as e:
        # Prints the error
        print(e)

        # If there's an error scanning the album, the light blinks quickly and then shuts off
        plynth_stop()

# Stops playing


def plynth_stop():
    MPDClient.stop()
    led.blink(on_time=0.2, off_time=0.2)
    sleep(2)
    led.off
    global current_scan
    current_scan = 0

# Safe shutdown of the Pi. The same button also starts up the Pi


def plynth_off():
    call("sudo shutdown -h now", shell=True)

# Uses Spotipy to search Spotify, without having to authenticate


def spotify_search(album_guess):
    spotify = spotipy.Spotify()
    results = spotify.search(q='album:' + album_guess, type='album', limit=5)
    albums = results['albums']['items']
    return albums


# All are the same button, set at different duractions
btn = Button(3, hold_time=2)
btn.when_pressed = plynth_scan
btn.when_held = plynth_stop

# Use these settings if you'd like to place your album on a
# switch to set off the scan, as opposed to pressing a button.
# You can still optionally add an on/off switch, controlled below.
# scan_button = Button(36)
# scan_button.when_pressed = plynth_scan
#stop_button.when_released = plynth_stop

# on/off button
# off_button = Button(5, hold_time=5)
# off_button.when_pressed = plynth_off

pause()
