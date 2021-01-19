# Spotify Lyrics Checker

# Checking Lyrics for Spotify Playlists
### Why?
As a host for campus radio, I'm constantly worried that I didn't screen my songs carefully enough, as this could incur fines or result in the cancelling of my show. Spotify's own explicit tag doesn't always reflect the contents of the songs in their entirety, so I needed to find some kind of solution. I had been checking them manually on Genius, but this took too much time and was still prone to mistakes. This motivated me to program a tool that could easily comb through a list of songs, check their lyrics for certain filter words, and then return a score reflecting its relative explicitness.
The first iteration of this idea was programmed entirely in Ruby, but I wanted to add a UI and some slightly better support for special characters, filtering, etc. The result isn't on GitHub, as it contains the credentials for accessing the Spotify API (I haven't tried to integrate user authentication yet).

### How?
Utilizing the Spotipy module for Python, the calls to the Spotify Web API are handled for me. I set up a developer account to gain access to the Spotify API programmatically. There is a slight drawback, since my code can't exactly be distributed with the private credentials in it. As such, the GitHub repo for this project (when created) will probably contain a pre-compiled executable until I can get the user authentication working properly.

The program takes in a Spotify URI to a public playlist and compiles a tracklist alongside the name of the artists. It then synthesizes the URLs to the Genius page for each song. It then scrapes the lyrics from the webpage utilizing BeautifulSoup and splits each song into component words. It then compares each word in the song to a user-defined dictionary (contained in a file named ```dict```) and computes a score.

The ```dict``` file contains filter words and their respective scores in the following format: ``` <filter word>,<score> ```. For obvious reasons, I will not be distributing a list of obscenities in the GitHub repo. Each score-word pair should be separated by a newline. The computed score is the addition of all individual filter word scores detected. 

As an added challenge, I implemented a basic user UI to accompany the code. I utilized Qt Designer and the PyQt5 library to manage the UI functionality. It has a text input box for the playlist URI and a button to trigger the rest of the program. The tabulated results for each song are displayed in a table above the textbox. To prevent the UI from going unresponsive, the scraping and filtering algorithm is threaded, such that there is one thread for each individual song. As a result, the program runs significantly faster and allows the UI to function properly and not lock up while the songs are being processed. 
