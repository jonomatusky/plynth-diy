A simple python program to turn your Raspberry Pi into a "record player", based on <a href="www.plynth.com">Plynth</a>. Uses the <a href="https://cloud.google.com/vision/docs/libraries#client-libraries-install-python">Google Vision API</a> as well as <a href="">Spotipy</a> to search and <a href="https://github.com/mopidy">Mopidy</a> to play Spotify on the Pi. Thanks to <a href="https://github.com/PatrickWeaver">Patrick Weaver</a> for inspiration on how to improve the Spofity search funtion, from his <a href="https://github.com/patrickweaver/record-player">record player</a> project.

To get this running, you'll first need to install Mopidy and add your Google crecentials as environmental varialbes and your Spotify credentials to the Mopidy configuration file.
