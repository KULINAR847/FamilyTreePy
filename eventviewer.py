# This Python file uses the following encoding: utf-8
import sys
import os
from sys import platform

from PySide2.QtWidgets import QApplication, QMenu, QAction, QDialog, QLabel, QFileDialog, QWidget, QGridLayout, QListWidget, QListWidgetItem, QInputDialog, QLineEdit, QMessageBox
from PySide2.QtCore import QTranslator, QLibraryInfo, Qt, QRect
from PySide2.QtGui import QFont, QGuiApplication, QImage, QPixmap

from driver import AllTables
from event_gallery import QLabelM
from personcard import QInvisibleButton
from dictionary import translate
from especialwidgets import DictViewer
#from video_player import VideoWindow

import subprocess

mainfont = QFont("Arial", 10)
rect = QRect(0, 0, 200, 200)

def get_by_key(d, key):
	return d[key] if type(d) == type({}) and key in d.keys() else 0

def compare_lists(l1, l2):
	if type(l1) == type(l2) == type([]):
		if len(l1) == len(l2):
			for e in l1:
				if e not in l2:
					return False
			return True
	return False

class EventViewer(QDialog):
	def __init__(self, alid=0, db=0, mode=0):
		super().__init__()
		self.font = mainfont		
		self.resize(1000, 600)
		layout = QGridLayout()
		self.layout = layout
		self.buttext = []
		self.dictViewer = QWidget()

		self.linedits = {}
		self.last_eid = 0
		self.photo_ids = 0
		self.QLABELM_TYPE = type(QLabelM())
			
				
		self.listWidget = QListWidget()
		self.listWidget.itemDoubleClicked.connect(self.doubleClick)
		self.listWidget.itemSelectionChanged.connect(self.itemChanged)

		self.setFont(mainfont)
		self.db = db		
		self.alid = alid
		self.event_ids = db.get_all_event_ids(self.alid)	
		self.photo_gallery = QLabel()
		#self.photo_gallery.setAlignment(Qt.AlignCenter)
		#self.photo_gallery.setPixmap(QPixmap('f.png').scaled(400,400,Qt.KeepAspectRatio))
		print(self.event_ids)
		if self.event_ids:
			for eid in self.event_ids:
				event = db.get_event_data(self.alid, eid)
				print(event)
				if event:					
					text = ''					
					text = event['event_head'] if type(event) == type({}) and 'event_head' in event.keys() and event['event_head'] != '' else text				
					item = QListWidgetItem(text)					
					if type(event) == type({}) and 'eid' in event.keys():
						item.setWhatsThis(str(event['eid']))
					self.listWidget.addItem(item)
			if self.listWidget.count():
				self.listWidget.setCurrentRow(0)

		self.mode = mode
		
		def openMenu(position):
			# Создание PopupMenu
			menu = QMenu()			
			if mode > 0:				
				addAction = menu.addAction('Добавить событие')
				#menu.addSeparator()
				editAction = menu.addAction('Переименовать событие')
				#menu.addSeparator()
				delAction = menu.addAction('Удалить событие')
				delAllAction = menu.addAction('Удалить все события')
				menu.addSeparator()
			else:
				addAction, editAction, delAction, delAllAction = QAction(), QAction(), QAction(), QAction()
			quitAction = menu.addAction('Выход')
			action = menu.exec_(self.mapToGlobal(position))
			
			# Привязка событий к Actions					
			if action == addAction:
				text, ok = QInputDialog().getText(self, "Название события",
								"Ввкдите название события:", QLineEdit.Normal, '')
				if ok:
					text = 'Новое событие' if text == '' else text
					res = self.db.add_event({'alid': self.alid, 'event_head': text})
					if len(res) == 1:
						event = res[0]
						text = event['event_head'] if type(event) == type({}) and 'event_head' in event.keys() and event['event_head'] != '' else 'Новое событие'
						item = QListWidgetItem(text)
						item.setWhatsThis(str(event['eid']))									
						self.listWidget.addItem(item)
						db.events.save()
						#self.changed = True			
				self.event_ids = db.get_all_event_ids(self.alid)	
				
			if action == editAction:
				eid = self.listWidget.currentItem()
				if eid is not None:					
					eid = self.listWidget.currentItem().whatsThis()	
					last_name = self.db.get_event_data(self.alid, eid)['event_head']		
					text, ok = QInputDialog().getText(self, "Название события",
						"Ввкдите новое название события:", QLineEdit.Normal, str(last_name))
					if ok:	
						event = self.db.edit_event({'alid': self.alid, 'eid': eid, 'event_head': text})
						self.listWidget.currentItem().setText(text)
						self.db.events.save()
						if event:
							event = self.db.get_event_data(alid, eid)
							#b = layout.takeAt(1)    
							self.dictViewer.close()				
							#b.widget().deleteLater()
							self.dictViewer = DictViewer(event, 1, self.db.events.invizible_fields, self.db.events.editable_fields)
							self.layout.addWidget(self.dictViewer, 0, 2)
					self.event_ids = db.get_all_event_ids(self.alid)	

			if action == delAction:
				res = QMessageBox.question(self, 'ВНИМАНИЕ!!!', "Вы действительно хотите удалить событие?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
				if res == QMessageBox.Yes:
					eid = self.listWidget.currentItem()
					if eid is not None:					
						eid = self.listWidget.currentItem().whatsThis()
						self.db.del_event({'alid':self.alid, 'eid': eid})
						self.listWidget.takeItem(self.listWidget.currentRow())
						self.db.events.save()
						#self.changed = True
					self.event_ids = db.get_all_event_ids(self.alid)	

			if action == delAllAction:
				res = QMessageBox.question(self, 'ВНИМАНИЕ!!!', "Вы действительно хотите удалить все события?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
				if res == QMessageBox.Yes:
					if self.db.del_all_events(int(self.alid)):
						self.listWidget.clear()
						self.db.events.save()
						#self.changed = True
					self.event_ids = db.get_all_event_ids(self.alid)	
					
					#db.photos.save()

			if action == quitAction:
				self.accept()

		self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)		  
		self.listWidget.customContextMenuRequested.connect(openMenu)	

		layout.addWidget(self.listWidget, 0, 0, 1, 1)
		layout.addWidget(self.photo_gallery, 0, 1, 1, 1)
				
		self.setLayout(layout)
			
	def doubleClick(self, item):
		if item is not None:		
			eid = item.whatsThis()				
			text = self.db.get_event_path(self.alid, eid)
			print(eid)

	def closeEvent(self, event):
		if self.last_eid:
			self.check_and_save(self.last_eid)

	def itemChanged(self):
		if self.last_eid:
			self.check_and_save(self.last_eid)
		
		eid = self.listWidget.currentItem()
		if eid is not None:					
			eid = self.listWidget.currentItem().whatsThis()
			event = self.db.get_event_data(self.alid, eid)

			if self.photo_gallery:
				self.photo_gallery.close()

			# Работаем с фотками
			self.photo_gallery = QLabelM(self.alid, self.db, 1, eid)
			self.layout.addWidget(self.photo_gallery, 0, 1, int(self.db.events.nkeys/2), 1)
			
			# Заполняем данными
			self.fill_event_data(event)
			
			print(event)	
			self.last_eid = eid
		self.setFocus()
		#print('item changed = ' + str(eid))

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Left:
			#print('left pressed')
			if type(self.photo_gallery) == self.QLABELM_TYPE:
				self.photo_gallery.prev_show()
		if event.key() == Qt.Key_Right:
			#print('right pressed')
			if type(self.photo_gallery) == self.QLABELM_TYPE:
				self.photo_gallery.next_show()
		#super().keyPressEvent(event)

	def fill_event_data(self, event):		
		if type(event) != type({}):
			return

		self.dictViewer.close()		
		self.dictViewer = DictViewer(event, 1, self.db.events.invizible_fields, self.db.events.editable_fields)
		self.layout.addWidget(self.dictViewer, 0, 2, 1, 1)
	
	def check_and_save(self, eid):				
		print('check_and_save' + str(eid))		
		changes = self.dictViewer.get_changes()
		event = self.db.get_event_data(self.alid, eid)
	
		if self.photo_gallery.changed:
			changes['photo_ids'] = self.photo_gallery.photo_ids
		print(changes)
		if len(changes) > 0 and type(event) == type({}):
			print('event changes saved')			
			event.update(changes)
			self.db.edit_event(event)
			self.db.events.save()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	app.setStyle('Fusion')
    
	db = AllTables('database/objects')	
	p = EventViewer(1, db, 1)
	p.show()

	sys.exit(app.exec_())