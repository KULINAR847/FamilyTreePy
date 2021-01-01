# This Python file uses the following encoding: utf-8
import sys
import os
from sys import platform

from PySide2.QtWidgets import QApplication, QMenu, QAction, QDialog, QLabel, QFileDialog, QWidget, QGridLayout, QListWidget, QListWidgetItem, QInputDialog, QLineEdit, QMessageBox
from PySide2.QtCore import QTranslator, QLibraryInfo, Qt, QRect
from PySide2.QtGui import QFont, QGuiApplication, QImage, QPixmap

from driver import AllTables
from album_gallery import QLabelMA
from especialwidgets import DictViewer
from eventviewer import EventViewer
import subprocess

mainfont = QFont("Arial", 10)
rect = QRect(0, 0, 200, 200)

class AlbumViewer(QDialog):
	def __init__(self, pid=0, db=0, mode=0):
		super().__init__()
		self.font = mainfont		
		self.resize(500,self.height())
		layout = QGridLayout()
		self.layout = layout
		self.buttext = []
		self.last_alid = 0
		
		self.listWidget = QListWidget()
		self.listWidget.itemDoubleClicked.connect(self.doubleClick)
		self.listWidget.itemSelectionChanged.connect(self.itemChanged)

		self.dictAlbum = QWidget()
		self.DICTVIEWERTYPE = type(DictViewer())
		self.setFont(mainfont)
		self.db = db		
		self.pid = pid
		self.album_ids = db.get_all_albums_ids()
		print(self.album_ids)
		if self.album_ids:			
			for alid in self.album_ids:
				album = db.get_album_data(alid)
				print(album)	
				self.dictAlbum = DictViewer(album, 1, self.db.albums.invizible_fields, self.db.albums.editable_fields)
				
				if album:
					text = ''					
					text = album['title'] if type(album) == type({}) and 'title' in album.keys() and album['title'] != '' else text
					item = QListWidgetItem(text)					
					if type(album) == type({}) and 'alid' in album.keys():
						item.setWhatsThis(str(album['alid']))
					self.listWidget.addItem(item)
			self.listWidget.setCurrentRow(0)
		self.mode = mode
		
		def openMenu(position):
			# Создание PopupMenu
			menu = QMenu()		  
			openAction = menu.addAction('Открыть альбом')
			openEAction = menu.addAction('Открыть события')
			menu.addSeparator()
			if mode > 0:
				#importAction = menu.addAction('Выгрузить альбом') 
				exportAction = menu.addAction('Добавить альбом')
				renameAction = menu.addAction('Переименовать альбом')
				#menu.addSeparator()
				#editAction = menu.addAction('Заменить')
				menu.addSeparator()
				delAction = menu.addAction('Удалить альбом')
				delAllAction = menu.addAction('Удалить все альбомы')
				menu.addSeparator()
			else:
				exportAction, delAction, delAllAction = QAction(), QAction(), QAction()
			quitAction = menu.addAction('Выход')
			action = menu.exec_(self.mapToGlobal(position))
			
			# Привязка событий к Actions
			if action == openAction:
				self.doubleClick(self.listWidget.currentItem())		

			if action == openEAction:
				item = self.listWidget.currentItem()
				if item is not None:		
					alid = item.whatsThis()
					self.events = EventViewer(int(alid), db, 1)
					self.events.show()
							
			if action == exportAction:
				text, ok = QInputDialog().getText(self, "Название альбома",
					"Ввкдите название альбома:", QLineEdit.Normal, 'Альбом')
				if ok:
					res = self.db.add_album({'imid': -1, 'title': text})
					if len(res) == 1:
						album = res[0]						
						item = QListWidgetItem(text)
						item.setWhatsThis(str(album['alid']))									
						self.listWidget.addItem(item)
				self.album_ids = db.get_all_albums_ids()

			if action == renameAction:
				item = self.listWidget.currentItem()
				if item is not None:		
					alid = item.whatsThis()
					album = db.get_album_data(alid)					
					text, ok = QInputDialog().getText(self, "Название альбома",
						"Ввкдите название альбома:", QLineEdit.Normal, album['title'])
					if ok:
						album = db.edit_album({'alid': int(alid), 'imid': -1, 'title': text})
						item.setText(text)
						if album:
							album = self.db.get_album_data(alid)
							# b = layout.takeAt(1)    
							# self.dictAlbum.close()				
							# b.widget().deleteLater()
							self.dictAlbum = DictViewer(album, 1, self.db.albums.invizible_fields, self.db.albums.editable_fields)
							self.layout.addWidget(self.dictAlbum, 0, 1)
						self.album_ids = db.get_all_albums_ids()
				
			if action == delAction:
				res = QMessageBox.question(self, 'ВНИМАНИЕ!!!', "Вы действительно хотите удалить альбом?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
				if res == QMessageBox.Yes:
					self.delete_item()	

			if action == delAllAction:
				res = QMessageBox.question(self, 'ВНИМАНИЕ!!!', "Вы действительно хотите удалить все альбомы?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
				if res == QMessageBox.Yes:
					item = self.listWidget.currentItem()
					while item is not None:
						self.delete_item()
						item = self.listWidget.currentItem()
					
					self.album_ids = db.get_all_albums_ids()

			if action == quitAction:
				self.accept()

		self.setContextMenuPolicy(Qt.CustomContextMenu)		  
		self.customContextMenuRequested.connect(openMenu)	

		layout.addWidget(self.listWidget, 0, 0)
		layout.addWidget(self.dictAlbum, 0, 1)
		
		self.setLayout(layout)

	def delete_item(self):
		item = self.listWidget.currentItem()
		if item is not None:
				
			alid = item.whatsThis()					
			self.db.del_album(int(alid))
			self.listWidget.takeItem(self.listWidget.currentRow())
			self.album_ids = self.db.get_all_albums_ids()


	def itemChanged(self):
		if self.last_alid:
			self.check_and_save(self.last_alid)
		
		item = self.listWidget.currentItem()
		if item is not None:		
			alid = item.whatsThis()	

			album = self.db.get_album_data(alid)	
			self.dictAlbum = DictViewer(album, 1, self.db.albums.invizible_fields, self.db.albums.editable_fields)
			self.layout.addWidget(self.dictAlbum, 0, 1)
			self.last_alid = alid
		self.setFocus()

	def doubleClick(self, item):
		if item is not None:		
			alid = item.whatsThis()
			print(alid)
			self.viewer = QLabelMA(alid, self.db, 1)
			self.viewer.show()

	def check_and_save(self, alid):							
		changes = self.dictAlbum.get_changes()
		album = self.db.get_album_data(alid)

		print(changes)
		if len(changes) > 0 and type(album) == type({}):
			print('album changes saved')			
			album.update(changes)
			self.db.edit_album(album)
			


if __name__ == '__main__':
	app = QApplication(sys.argv)
	app.setStyle('Fusion')
    
	db = AllTables('database/objects')
	people = db.get_people(1)
	p = AlbumViewer(people['pid'], db, 1)
	p.show()

	sys.exit(app.exec_())