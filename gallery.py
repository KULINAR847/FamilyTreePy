# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2 import QtCore, QtGui, QtWidgets

from driver import AllTables, Files
import datetime
import base64

def file_to_base64(filename):
	with open(filename, 'rb') as image_file:
		return base64.b64encode(image_file.read())	

def base64_to_file(filename, data):	
	with open(filename, 'wb') as f:
		f.write(base64.b64decode(data))
		return True
	return False

def base64_to_image(base_str):
	pix = QPixmap()
	if pix.loadFromData(QByteArray.fromBase64(base_str)):
		return pix
	return QPixmap()

class Gallery(QDialog):
	def __init__(self, pid=0, db=0, mode=0):
		super().__init__()

		screen = QGuiApplication.primaryScreen()
		screenSize = screen.availableSize()
		height = screenSize.height()
		self.height = height
		width = screenSize.width()
		self.width = width
		self.setGeometry(0, 0, width, height)
		
		self.db = db
		self.pid = int(pid)
		self.photo_ids = db.get_all_photo_ids(pid) # phid s

		self.photo = QLabel(self)
		self.photo.setGeometry(0, 0, width, height)
		self.photo.setAlignment( Qt.AlignVCenter | Qt.AlignHCenter )
		self.next_photo = QPushButton('>', self)
		self.next_photo.clicked.connect(self.next_show)		
		self.next_photo.setStyleSheet('''QPushButton { font-size:0; color: white; }  QPushButton:hover { color: green; font-size:100pt;}''') 		
		self.next_photo.setGeometry(width - width/10, 0, width/10, height)
		self.prev_photo = QPushButton('<', self)
		self.prev_photo.setStyleSheet('''QPushButton { font-size:0; color: white; }  QPushButton:hover { color: green; font-size:100pt;}''')
		self.prev_photo.setGeometry(0, 0, width/10, height)
		self.prev_photo.clicked.connect(self.prev_show)

		self.curpixmap = 0
		self.curindex = 0
		if self.photo_ids and len(self.photo_ids) > 0:
			path = self.db.get_photo_path(self.pid, self.photo_ids[0])
			if path:
				self.curpixmap = QPixmap(path)
		
		#self.count = len(self.photo_ids) if type(self.photo_ids) == type([]) else 0
		self.mode = mode
		self.pixmap = self.curpixmap
		#if self.count > 0:
		#	minlid = max( self.images.keys() )
		if self.curpixmap:
			self.photo.setPixmap(self.pixmap.scaled(self.width-20, self.height-20, Qt.KeepAspectRatio))

		def openMenu(position):
			menu = QMenu()		  
			viewAction = menu.addAction('Информация')
			if mode > 0:
				importAction = menu.addAction('Выгрузить фото') 
				exportAction = menu.addAction('Загрузить фото')
				editAction = menu.addAction('Заменить')
				delAction = menu.addAction('Удалить')
				delAllAction = menu.addAction('Удалить все')
			else:
				importAction, exportAction, editAction, delAction, delAllAction = QAction(), QAction(), QAction(), QAction(), QAction()
			quitAction = menu.addAction('Выход')
			action = menu.exec_(self.mapToGlobal(position))
			if action == viewAction:
				pass

			if action == importAction:
				if self.photo_ids and type(self.photo_ids) == type([]) and len(self.photo_ids) > 0:					
					dialog = QFileDialog()
					path = self.db.get_photo_path(self.pid, self.photo_ids[self.curindex])
					oldfilename = os.path.basename( path )	
					_, ext = os.path.splitext(path)				
					filename = QFileDialog.getSaveFileName(self, "Сохранить", oldfilename, 'Изображение (*' + ext + ')')  
					print(filename)
					if filename[0] != '':										
						print('Запись успешна = ' + str( self.curpixmap.toImage().save(filename[0])	))	
							
			if action == exportAction:
				dialog = QFileDialog()
				dialog.setFileMode(QFileDialog.ExistingFiles)
				img_filter = 'Изображения (*.png *.bmp *.jpg);'
				dialog.setNameFilter(img_filter)
				fileNames = []
				if (dialog.exec()):
					  fileNames = dialog.selectedFiles()
				if len(fileNames) > 0:
					#print(fileNames)
					last_len = len(self.photo_ids) if type(self.photo_ids) == type([]) else 0
					for i, f in enumerate(fileNames):
						if os.path.isfile(f):
							self.db.add_photo({'pid': self.pid, 'oldpath': f})
					self.photo_ids = db.get_all_photo_ids(self.pid)		
					if self.photo_ids and type(self.photo_ids) == type([]) and len(self.photo_ids) > 0:
						if last_len < len(self.photo_ids):
							self.curindex = last_len
						else:
							self.curindex = 0
						path = self.db.get_photo_path(self.pid, self.photo_ids[self.curindex])
						if path:
							pixmap = QPixmap(path)
							self.photo.setPixmap(pixmap.scaled(self.width-20, self.height-20, Qt.KeepAspectRatio))
							self.curpixmap = pixmap		
			
			if action == editAction:
				if self.photo_ids and type(self.photo_ids) == type([]) and len(self.photo_ids) > 0:				
					dialog = QFileDialog()
					#dialog.setFileMode(QFileDialog.ExistingFiles)
					img_filter = 'Изображения (*.png *.bmp *.jpg);'
					dialog.setNameFilter(img_filter)
					fileNames = []
					if (dialog.exec()):
						fileNames = dialog.selectedFiles()
					if len(fileNames) == 1:
						print(fileNames[0])
						self.db.edit_photo({'pid':self.pid, 'phid': self.photo_ids[self.curindex], 'oldpath': fileNames[0]})
						path = self.db.get_photo_path(self.pid, self.photo_ids[self.curindex])
						if path:
							pixmap = QPixmap(path)
							self.photo.setPixmap(pixmap.scaled(self.width-20, self.height-20, Qt.KeepAspectRatio))
							self.curpixmap = pixmap
				else:
					self.photo.setPixmap(QPixmap())
					self.curpixmap = QPixmap()

			if action == delAction:
				if self.photo_ids and type(self.photo_ids) == type([]) and len(self.photo_ids) > 0:
					self.db.del_photo({'pid':self.pid, 'phid': self.photo_ids[self.curindex]})
					self.photo_ids = db.get_all_photo_ids(self.pid)	
					if self.photo_ids and type(self.photo_ids) == type([]) and len(self.photo_ids) > 0:
						if self.curindex >= len(self.photo_ids):
							self.curindex = len(self.photo_ids) - 1
						path = self.db.get_photo_path(self.pid, self.photo_ids[self.curindex])
						if path:
							pixmap = QPixmap(path)
							self.photo.setPixmap(pixmap.scaled(self.width-20, self.height-20, Qt.KeepAspectRatio))
							self.curpixmap = pixmap	
						else:
							self.photo.setPixmap(QPixmap())
							self.curpixmap = QPixmap()
					else:
						self.photo.setPixmap(QPixmap())
						self.curpixmap = QPixmap()
				else:
					self.photo.setPixmap(QPixmap())
					self.curpixmap = QPixmap()	


			if action == delAllAction:
				if self.db.del_all_photo(self.pid):
					self.photo.setPixmap(QPixmap())
					self.curpixmap = QPixmap()
					#db.photos.save()

			if action == quitAction:
				self.accept()

		self.setContextMenuPolicy(Qt.CustomContextMenu)		  
		self.customContextMenuRequested.connect(openMenu)	
	
		#layout.addWidget(self.photo, 0, 0, 4, 4)
		#layout.addWidget(self.next_photo, 0, 0, 4, 4)
		#layout.addWidget(self.prev_photo, 0, 0, 8, 1)


		#self.setLayout(layout)

	def get_follow_image_by_index(self, direct=1):
		step = direct
		#print('curind do = ' +  str(self.curindex))
		if self.photo_ids and len(self.photo_ids) > 0:
			next_index = self.curindex + step
			if next_index < len(self.photo_ids) and next_index >= 0:				
				self.curindex = next_index
			elif next_index == len(self.photo_ids):
				self.curindex = 0
			elif next_index < 0:
				self.curindex = len(self.photo_ids) - 1

			path = self.db.get_photo_path(self.pid, self.photo_ids[self.curindex])
			return QPixmap(path)
		return QPixmap()

	def next_show(self):
		#print('next_pressed')
		pixmap = self.get_follow_image_by_index()
		self.photo.setPixmap(pixmap.scaled(self.width-20, self.height-20, Qt.KeepAspectRatio))
		self.curpixmap = pixmap
		#self.setWindowTitle(self.windowTitle() + '.')
		#print('curpix after = ' +  str(self.curpixind))

	def prev_show(self):
		#print('prev_pressed')
		pixmap = self.get_follow_image_by_index(-1)
		self.photo.setPixmap(pixmap.scaled(self.width-20, self.height-20, Qt.KeepAspectRatio))
		self.curpixmap = pixmap
		#self.setWindowTitle(self.windowTitle() + '-')
		#print('curpix after = ' +  str(self.curpixind))


if __name__ == '__main__':
	app = QApplication(sys.argv)

	database = AllTables('database/objects')
	g = Gallery(1, database, 1)
	#g = Gallery(0, 0, 0)
	g.showMaximized()

	sys.exit(app.exec_())