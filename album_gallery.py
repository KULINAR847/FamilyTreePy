# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2.QtWidgets import QApplication, QMenu, QAction, QDialog, QLabel, QHBoxLayout, QFrame, QFileDialog, QWidget, QGridLayout, QListWidget, QListWidgetItem
from PySide2.QtCore import QTranslator, QLibraryInfo, Qt, QRect
from PySide2.QtGui import QFont, QGuiApplication, QImage, QPixmap

from driver import AllTables, Files
from especialwidgets import DictViewer
from video_player import VideoWindow
import datetime

def get_by_key(d, key):
	return d[key] if type(d) == type({}) and key in d.keys() else 0

class QLabelMA(QWidget):
	def __init__(self, alid=0, db=0, mode=0, parent=None):
		super().__init__(parent)

		self.db = db
		self.alid = int(alid)		
		self.curindex = 0
		self.viewWidget = QLabel()
		layout = QGridLayout()
		self.layout = layout


		#event = db.get_event_data(self.alid, self.eid) if db else 0
		self.photo_ids = db.get_all_albums_photos(self.alid)
		print('self.photo_ids')
		print(self.photo_ids)
		
		self.setPhoto()
		self.mode = mode
		
		def openMenu(position):
			# Создание PopupMenu
			menu = QMenu()			
			if mode > 0:				
				addAction = menu.addAction('Добавить фото')
				addAction2 = menu.addAction('Добавить видео')
				#menu.addSeparator()
				nextAction = menu.addAction('Следующий')
				#menu.addSeparator()
				delAction = menu.addAction('Удалить фото')
				delAllAction = menu.addAction('Удалить все фото')
				menu.addSeparator()
			else:
				addAction, addAction2, delAction, delAllAction = QAction(), QAction(), QAction(), QAction()
			quitAction = menu.addAction('Выход')
			action = menu.exec_(self.mapToGlobal(position))
			
			# Привязка событий к Actions					
			if action == addAction:
				res = []
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
							data = self.db.add_album({'alid': self.alid, 'oldpath': f})
							if data:
								if self.photo_ids:
									self.photo_ids.append( data[0]['imid'] )
								else:
									self.photo_ids = [ data[0]['imid'] ]							
					print(self.photo_ids)					
					if self.photo_ids and type(self.photo_ids) == type([]) and len(self.photo_ids) > 0:
						if last_len < len(self.photo_ids):
							self.curindex = last_len
						else:
							self.curindex = 0
						self.setPhoto()

			if action == addAction2:
				res = []
				dialog = QFileDialog()
				dialog.setFileMode(QFileDialog.ExistingFiles)
				img_filter = 'Видео (*.mp4 *.avi *.3gp *.mpeg *.mpg);'
				dialog.setNameFilter(img_filter)
				fileNames = []
				if (dialog.exec()):
					  fileNames = dialog.selectedFiles()
				if len(fileNames) > 0:
					#print(fileNames)
					last_len = len(self.photo_ids) if type(self.photo_ids) == type([]) else 0
					for i, f in enumerate(fileNames):
						if os.path.isfile(f):
							data = self.db.add_album({'alid': self.alid, 'oldpath': f, 'video': True})
							if data:
								if self.photo_ids:
									self.photo_ids.append( data[0]['imid'] )
								else:
									self.photo_ids = [ data[0]['imid'] ]							
					print(self.photo_ids)					
					if self.photo_ids and type(self.photo_ids) == type([]) and len(self.photo_ids) > 0:
						if last_len < len(self.photo_ids):
							self.curindex = last_len
						else:
							self.curindex = 0
						self.setPhoto()
				
			if action == nextAction:
				self.setFocus()
				self.next_show()

			if action == delAction:
				if self.photo_ids and type(self.photo_ids) == type([]) and len(self.photo_ids) > 0:
					self.db.del_photo_from_album({'alid': self.alid, 'imid': self.photo_ids[self.curindex]})
					self.photo_ids = db.get_all_albums_photos(self.alid)	
					if self.photo_ids and type(self.photo_ids) == type([]) and len(self.photo_ids) > 0:
						if self.curindex >= len(self.photo_ids):
							self.curindex = len(self.photo_ids) - 1
						self.setPhoto()							
					else:
						self.viewWidget.setPixmap(QPixmap( os.path.join( 'images', 'no-photo.jpg') ).scaled(400, 400, Qt.KeepAspectRatio))						
				else:
					self.viewWidget.setPixmap(QPixmap( os.path.join( 'images', 'no-photo.jpg') ).scaled(400, 400, Qt.KeepAspectRatio))
						

			if action == delAllAction:
				for imid in self.photo_ids:									
					self.db.del_photo_from_album({'alid': self.alid, 'imid': imid})	
				self.viewWidget.setPixmap(QPixmap( os.path.join( 'images', 'no-photo.jpg') ).scaled(400, 400, Qt.KeepAspectRatio))				
				self.photo_ids = db.get_all_albums_photos(self.alid)


			if action == quitAction:
				self.accept()

		self.setContextMenuPolicy(Qt.CustomContextMenu)		  
		self.customContextMenuRequested.connect(openMenu)

		layout.addWidget(self.viewWidget, 0, 0)
		#layout.addWidget(self.dictAlbum, 0, 1)
		
		self.setLayout(layout)

	def get_follow_image_by_index(self, direct=1):
		step = direct
		is_video = False
		#print('curind do = ' +  str(self.curindex))
		if self.photo_ids and len(self.photo_ids) > 0:
			next_index = self.curindex + step
			#print(next_index)
			#print(len(self.photo_ids))
			if next_index < len(self.photo_ids) and next_index >= 0:				
				self.curindex = next_index
			elif next_index == len(self.photo_ids):
				self.curindex = 0
			elif next_index < 0:
				self.curindex = len(self.photo_ids) - 1
			#print(self.curindex)

			data = self.db.get_album_data(self.alid, self.photo_ids[self.curindex])
			if type(data) == type({}) and 'video' in data.keys() and data['video']:
				is_video = True
			path = self.db.get_album_photo_path(self.alid, self.photo_ids[self.curindex])
			if is_video:				
				return path, is_video
			else:
				return QPixmap(path).scaled(400, 400, Qt.KeepAspectRatio), is_video
		return QPixmap( os.path.join( 'images', 'no-photo.jpg') ).scaled(400, 400, Qt.KeepAspectRatio), is_video

	def next_show(self):
		#print('next_pressed')
		pixmap, is_video = self.get_follow_image_by_index()
		#print('is_video = ' + str(is_video) )
		if is_video: 
			self.viewWidget.close()
			
			self.viewWidget = VideoWindow(pixmap, self)
			self.layout.addWidget(self.viewWidget, 0, 0)

		else:
			self.viewWidget.close()

			self.viewWidget = QLabel()
			self.viewWidget.setPixmap(pixmap)
			self.layout.addWidget(self.viewWidget, 0, 0)			
			self.curpixmap = pixmap


	def prev_show(self):
		#print('prev_pressed')
		pixmap, is_video = self.get_follow_image_by_index(-1)
		if is_video: 
			self.viewWidget.close()
			
			self.viewWidget = VideoWindow(pixmap, self)			
			self.layout.addWidget(self.viewWidget, 0, 0)			
		else:			
			self.viewWidget.close()			

			self.viewWidget = QLabel()
			self.viewWidget.setPixmap(pixmap)
			self.layout.addWidget(self.viewWidget, 0, 0)			
			self.curpixmap = pixmap

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Left:
			self.prev_show()
		if event.key() == Qt.Key_Right:
			self.next_show()
		#super().keyPressEvent(event)

	def setPhoto(self):
		if self.photo_ids:
			if type(self.photo_ids) == type([]) and len(self.photo_ids) > 0:
				path = self.db.get_album_photo_path(self.alid, self.photo_ids[self.curindex])
				if path:
					data = self.db.get_album_data(self.alid, self.photo_ids[self.curindex])
					if type(data) == type({}) and 'video' in data.keys() and data['video']:
						self.viewWidget.close()	
						self.viewWidget = VideoWindow(path, self)
						self.layout.addWidget(self.viewWidget, 0, 0)
						self.resize(500,500)
					else:
						self.viewWidget.setPixmap(QPixmap(path).scaled(400, 400, Qt.KeepAspectRatio))
				else:
					self.viewWidget.setPixmap(QPixmap( os.path.join( 'images', 'no-photo.jpg') ).scaled(400, 400, Qt.KeepAspectRatio))
		else:
			self.viewWidget.setPixmap(QPixmap( os.path.join( 'images', 'no-photo.jpg') ).scaled(400, 400, Qt.KeepAspectRatio))
		self.setFocus()


if __name__ == '__main__':
	app = QApplication(sys.argv)

	database = AllTables('database/objects')
	g = QLabelM(1, database, 1)
	#g = Gallery(0, 0, 0)
	g.showMaximized()

	sys.exit(app.exec_())