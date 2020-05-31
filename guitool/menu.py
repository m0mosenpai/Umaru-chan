#!/usr/bin/env python3
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import qdarkstyle
import json

#Widget class for elements in the window
class Widget(QWidget):
	def __init__(self):
		QWidget.__init__(self)

		self.items = 0

		#Get watchlist data
		config = getConfig()
		anames = list(config['watchlist'].keys())
		latestEps = [] 
		for i in list(config['watchlist'].values()):
			latestEps.append(int(i[0]))
		watchlist = list(zip(anames, latestEps))
		watchlist.sort()

		self._data = dict(watchlist)
		
		self.setWindowTitle("Watchlist")
		self.resize(700, 500)

		#Left
		self.table = QTableWidget()
		self.table.setColumnCount(2)
		self.table.setHorizontalHeaderLabels(["Anime Name", "Latest Episode Downloaded"])
		self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

		#Right
		self.name = QLineEdit()
		self.ep = QLineEdit()
		self.add = QPushButton("Add")
		self.clear = QPushButton("Clear")
		self.quit = QPushButton("Quit")

		self.right = QVBoxLayout()
		self.right.setContentsMargins(10, 10, 10, 10)
		self.right.addWidget(QLabel("Anime Name"))
		self.right.addWidget(self.name)
		self.right.addWidget(QLabel("Latest Episode Downloaded"))
		self.right.addWidget(self.ep)
		self.right.addWidget(self.add)
		self.right.addStretch()
		self.right.addWidget(self.clear)
		self.right.addWidget(self.quit)

		#QWidget Layout
		self.layout = QHBoxLayout()
		self.layout.addWidget(self.table)
		self.setLayout(self.layout)
		self.fill_table()

		self.add.clicked.connect(self.add_element)
		self.quit.clicked.connect(self.quit_application)
		self.clear.clicked.connect(self.clear_table)

	#Adds a new element to the table
	def add_element(self):
		name = self.name.text()
		ep = self.ep.text()

		self.table.insertRow(self.items)
		self.table.setItem(self.items, 0, QTableWidget(name))
		self.table.setItem(self.items, 1, QTableWidget(ep))

		self.name.setText("")
		self.ep.setText("0")

		self.items += 1

	#Slot to clear table	
	@pyqtSlot()	
	def clear_table(self):
		self.table.setRowCount(0)
		self.items = 0

	@pyqtSlot()
	def quit_application(self):
		QApplication.quit()

	#Displays the table	
	def fill_table(self, data=None):
		data = self._data if not data else data
		for name, ep in data.items():
			self.table.insertRow(self.items)
			self.table.setItem(self.items, 0, QTableWidgetItem(name))
			self.table.setItem(self.items, 1, QTableWidgetItem(str(ep)))
			self.items += 1

#Defines structure of main window
class MainWindow(QMainWindow):
	def __init__(self, checked):
		QMainWindow.__init__(self)
		self.setWindowTitle("Umaru-chan")

		#Menu
		self.menu = self.menuBar()
		self.file_menu = self.menu.addMenu("File")

		#Exit QAction
		exit_action = QAction("Exit", self)
		exit_action.setShortcut("Ctrl+Q")
		exit_action.triggered.connect(self.exit_app)

		self.file_menu.addAction(exit_action)

	#Slot to exit application	
	@pyqtSlot()
	def exit_app(self):
		QApplication.quit()

#Return config from source/data/config.json
def getConfig():
	with open('../source/data/config.json', 'r') as f:
		config = json.load(f)
	return config

def main():
	# create the application and the main window
	app = QApplication(sys.argv)

	#QWidget
	widget = Widget()
	widget.show()

	#Creating main window
	window = MainWindow(widget)
	window.resize(800, 600)
	window.show()

	# setup stylesheet (dark theme)
	app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

	#Execute Application
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()