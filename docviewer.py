# This Python file uses the following encoding: utf-8
import sys
import os
from sys import platform

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from driver import AllTables
import subprocess

mainfont = QFont("Arial", 10)
rect = QRect(0, 0, 200, 200)

class DocViewer(QDialog):
	def __init__(self, pid=0, db=0, mode=0):
		super().__init__()
		self.font = mainfont		
		self.resize(500,self.height())
		layout = QGridLayout()
		self.buttext = []
		
		self.listWidget = QListWidget()
		self.listWidget.itemDoubleClicked.connect(self.doubleClick)

		self.setFont(mainfont)
		self.db = db		
		self.pid = pid
		self.docs_ids = db.get_all_doc_ids(self.pid)	
		#print(self.db.docs)
		if self.docs_ids:
			for did in self.docs_ids:
				doc = db.get_doc_data(self.pid, did)
				print(doc)
				if doc:
					text = ''					
					text = doc['desc'] if type(doc) == type({}) and 'desc' in doc.keys() and doc['desc'] != '' else text
					text = text + ' [' + str(os.path.basename(doc['oldpath'])) + ']' if type(doc) == type({}) and 'oldpath' in doc.keys() and doc['oldpath'] != '' else text
					text = text if text != '' else db.get_doc_path(self.pid, did)					
					item = QListWidgetItem(text)					
					if type(doc) == type({}) and 'did' in doc.keys():
						item.setWhatsThis(str(doc['did']))
					self.listWidget.addItem(item)
		self.mode = mode
		
		def openMenu(position):
			# Создание PopupMenu
			menu = QMenu()		  
			openAction = menu.addAction('Открыть документ')
			menu.addSeparator()
			if mode > 0:
				importAction = menu.addAction('Выгрузить документ') 
				exportAction = menu.addAction('Загрузить документ')
				menu.addSeparator()
				editAction = menu.addAction('Заменить')
				menu.addSeparator()
				delAction = menu.addAction('Удалить')
				delAllAction = menu.addAction('Удалить все')
				menu.addSeparator()
			else:
				importAction, exportAction, editAction, delAction, delAllAction = QAction(), QAction(), QAction(), QAction(), QAction()
			quitAction = menu.addAction('Выход')
			action = menu.exec_(self.mapToGlobal(position))
			
			# Привязка событий к Actions
			if action == openAction:
				self.doubleClick(self.listWidget.currentItem())		

			if action == importAction:
				did = self.listWidget.currentItem()
				if did is not None:
					did = self.listWidget.currentItem().whatsThis()					
					dialog = QFileDialog()
					path = self.db.get_doc_path(self.pid, did)
					doc_data = self.db.get_doc_data(self.pid, did)
					oldfilename = os.path.basename(doc_data['oldpath']) if type(doc_data) == type({}) and 'oldpath' in doc_data.keys() and doc_data['oldpath'] != '' else ''
					oldfilename = os.path.basename( path ) if oldfilename == '' else oldfilename	
					_, ext = os.path.splitext(path)				
					filename = QFileDialog.getSaveFileName(self, "Сохранить", oldfilename, 'Изображение (*' + ext + ')')  
					print(filename)
					if filename[0] != '':					
						print(filename[0])
						db.save_doc(path, filename[0])				
						#print('Запись успешна = ' + str( self.curpixmap.toImage().save(filename[0])	))	
							
			if action == exportAction:
				dialog = QFileDialog()
				dialog.setFileMode(QFileDialog.ExistingFiles)
				#img_filter = 'Изображения (*.png *.bmp *.jpg);'
				#dialog.setNameFilter(img_filter)
				fileNames = []
				if (dialog.exec()):
					  fileNames = dialog.selectedFiles()
				if len(fileNames) > 0:
					#print(fileNames)
					last_len = len(self.docs_ids) if type(self.docs_ids) == type([]) else 0
					for i, f in enumerate(fileNames):
						if os.path.isfile(f):

							text, ok = QInputDialog().getText(self, "Описание файла",
								"Ввкдите описание файла:", QLineEdit.Normal, 'Автобиография')
							if ok:
								res = self.db.add_doc({'pid': self.pid, 'oldpath': f, 'desc': text})
								if len(res) == 1:
									doc = res[0]
									text = text + ' [' + str(os.path.basename(doc['oldpath'])) + ']' if type(doc) == type({}) and 'oldpath' in doc.keys() and doc['oldpath'] != '' else text
									item = QListWidgetItem(text)
									item.setWhatsThis(str(doc['did']))									
									self.listWidget.addItem(item)
							else:
								res = self.db.add_doc({'pid': self.pid, 'oldpath': f})
								if len(res) == 1:
									item = QListWidgetItem(f)
									item.setWhatsThis(str(res[0]['did']))	
									self.listWidget.addItem(item)
				self.docs_ids = db.get_all_doc_ids(self.pid)	
				
			if action == editAction:
				did = self.listWidget.currentItem()
				if did is not None:					
					did = self.listWidget.currentItem().whatsThis()			
					dialog = QFileDialog()
					#dialog.setFileMode(QFileDialog.ExistingFiles)
					#img_filter = 'Изображения (*.png *.bmp *.jpg);'
					#dialog.setNameFilter(img_filter)
					fileNames = []
					if (dialog.exec()):
						fileNames = dialog.selectedFiles()
					if len(fileNames) == 1:
						print(fileNames[0])
						self.db.edit_doc({'pid':self.pid, 'did': did, 'oldpath': fileNames[0]})

			if action == delAction:
				did = self.listWidget.currentItem()
				if did is not None:					
					did = self.listWidget.currentItem().whatsThis()
					self.db.del_doc({'pid':self.pid, 'did': did})
					self.listWidget.takeItem(self.listWidget.currentRow())
				self.docs_ids = db.get_all_doc_ids(self.pid)	

			if action == delAllAction:
				if self.db.del_all_docs(int(self.pid)):
					self.listWidget.clear()
				self.docs_ids = db.get_all_doc_ids(self.pid)	
					
					#db.photos.save()

			if action == quitAction:
				self.accept()

		self.setContextMenuPolicy(Qt.CustomContextMenu)		  
		self.customContextMenuRequested.connect(openMenu)	

		layout.addWidget(self.listWidget, 0, 0)
		
		self.setLayout(layout)
			
	def doubleClick(self, item):
		if item is not None:		
			did = item.whatsThis()				
			text = self.db.get_doc_path(self.pid, did)
			if text:
				if "win32" in platform:
					subprocess.call('explorer ' + str(text), shell=True)	
				else:
					print('error unknown platform')	

	def read_binary(self, filename):
		with open(filename, 'rb') as f:
			return f.read()

	def write_binary(self, filename, data):
		with open(filename, 'wb') as f:
			return f.write(data)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	app.setStyle('Fusion')
    
	db = AllTables('database/objects')
	people = db.get_people(1)
	p = DocViewer(people['pid'], db, 1)
	p.show()

	sys.exit(app.exec_())