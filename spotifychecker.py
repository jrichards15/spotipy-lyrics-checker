from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt

import spotipy, requests, json
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from threading import Thread

class GeniusScraper:
	@staticmethod
	def init_dict(filename):
		f = open(filename)
		swears = {}

		for line in f:
			temp = line.split(",")
			swears[temp[0]] = int(temp[1])

		f.close()
		return swears	

	def __init__(self, song, artist):
		self.trns = str.maketrans("ÀÁÂÃÄaaaaaÈÉÊËèéêëÌÍÎÏìíîïÒÓÔÕÖòóôõöÙÚÛÜùúûüÑñÝŸýÿ",
								  "AAAAAaaaaaEEEEeeeeIIIIiiiiOOOOOoooooUUUUuuuuNnYYyy")
		self.swears = GeniusScraper.init_dict("dict")
		self.artist_name = artist.replace(" ", "-").lower().translate({ord('\'') : None, ord(',') : None}).translate(self.trns).capitalize()
		self.song_name = song
		self.process_song = song.replace(" ","-").lower().translate({ord('\'') : None, ord(',') : None}).translate(self.trns)
		self.url = 'http://genius.com/' + self.artist_name + '-' + self.process_song + '-lyrics'

	def get_lyrics(self):
		page = requests.get(self.url)
		soup = BeautifulSoup(page.text, 'html.parser')
		lyrics = soup.find("div",class_="lyrics")

		if lyrics is None:
			return ""
		else:
			return lyrics.get_text()

	def process_lyrics(self, lyrics):
		score = 0
		if lyrics is None or len(lyrics) == 0:
			return -1
		else:
			words = lyrics.split()
			for word in words:
				if word in self.swears:
					score = self.swears[word] + score
			return score

class PlaylistFinder:
	def __init__(self, uri):
		self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="",client_secret=""))
		self.id = uri

	def get_playlist(self):
		results = []
		temp = self.sp.playlist_tracks(self.id, fields='items.track.name,items.track.artists.name', additional_types=('track',))

		for track in temp['items']:
			artists = []
			for artist in track['track']['artists']:
				artists.append(artist['name'])
			results.append((track['track']['name'], artists))
		
		return results

class TabulatorThread:
	@staticmethod
	def get_score(combo):
		gs = GeniusScraper(combo[0], combo[1][0])
		result = gs.process_lyrics(gs.get_lyrics())

		if result > 0:
			print(combo[0],",",combo[1][0],",",result)
		return [combo[0], combo[1][0], result]

class SwearTabulator:
	def __init__(self, uri):
		self.id = uri
		self.pf = PlaylistFinder(self.id)

	def get_score(self):
		pl = self.pf.get_playlist()
		lst = []
		score = 0

		for (song,artists) in pl:
			gs = GeniusScraper(song, artists[0])
			result = gs.process_lyrics(gs.get_lyrics())
			
			if result > 0:
				print(song,",",artists[0],",",result)
			score += result

			lst.append([song, artists[0], result])

		print("Total Score: ", score)
		return lst

	def tabulate_scores(self):
		pl = self.pf.get_playlist()
		score = 0
		lst = []

		with ThreadPoolExecutor(max_workers = 5) as executor:
			results = executor.map(TabulatorThread.get_score, pl)
		
		for result in results:
			lst.append(result)
		return lst

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])
 
class TableThread(QtCore.QThread):
	finished_scanning = QtCore.pyqtSignal(object)

	def __init__(self, ins):
		QtCore.QThread.__init__(self)
		self.ins = ins

	def run(self):
		st = SwearTabulator(self.ins)
		results = st.tabulate_scores()

		self.finished_scanning.emit(results)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(468, 642)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(9, 9, 451, 591))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableView = QtWidgets.QTableView(self.verticalLayoutWidget)
        self.tableView.setObjectName("tableView")
        self.verticalLayout.addWidget(self.tableView)
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.input = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.input.setObjectName("input")
        self.verticalLayout.addWidget(self.input)
        self.pushButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 468, 18))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Spotify Lyrics Checker"))
        self.label.setText(_translate("MainWindow", "Spotify Playlist URI:"))
        self.pushButton.setText(_translate("MainWindow", "Find Swears!"))

class CheckerUI(QtWidgets.QMainWindow):
	def __init__(self):
		super(CheckerUI, self).__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)

		self.table = self.findChild(QtWidgets.QTableView, 'tableView')
		self.userin = self.findChild(QtWidgets.QLineEdit, 'input')

		self.button = self.findChild(QtWidgets.QPushButton, 'pushButton')
		self.button.clicked.connect(self.pressed_boi)

		self.worker = None
		self.show()

	def update_table(self, output):
		model = TableModel(output)
		self.table.setModel(model)

	def pressed_boi(self):
		ins = self.userin.text()
		if ins != "":
			self.worker = TableThread(ins)
			self.worker.finished_scanning.connect(self.update_table)
			self.worker.start()

def main():
	app = QApplication([])
	window = CheckerUI()
	app.exec_()

main()
