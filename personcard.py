# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2.QtWidgets import QApplication, QGridLayout, QPushButton, QTextEdit, QLineEdit, QDialog 
from PySide2.QtCore import QTranslator, QLibraryInfo, Qt, QRect
from PySide2.QtGui import QFont, QPixmap

from dictionary import translate
from docviewer import DocViewer
from gallery import Gallery
from driver import AllTables

mainfont = QFont("Arial", 10)
rect = QRect(0, 0, 200, 200)

class QInvisibleButton(QPushButton):
	def __init__(self, text='',parent = None):
		super().__init__(parent)
		self.setFlat(True)
		self.setText(text)
		self.setStyleSheet("* { background-color: rgba(0,0,0,100); color: rgba(0,0,0,100); text-align:right; }")

class PersonalCard(QDialog):
	def __init__(self, people=0, db=0, mode=0):
		super().__init__()
		self.font = mainfont		
		self.resize(700,self.height())
		layout = QGridLayout()
		self.buttext = []
		
		self.db = db
		self.people = people
		#print(people)
		self.pid = self.people['pid']
		self.edit_people = db.edit_people
		self.mode = mode
		self.gallery = Gallery(self.pid, self.db, mode)
		self.docviewer = DocViewer(self.pid, self.db, self.mode)
		#self.photos = self.gallery.curpixmap
		#print(self.photos)
		

		self.photo = QPushButton()
		if self.gallery.curpixmap:
			self.pixmap = QPixmap(self.gallery.curpixmap)
			#self.photofile = self.photo
		else:
			self.pixmap = QPixmap( os.path.join('images', 'f.png') )					
		self.change_icon()
		self.photo.clicked.connect(self.show_photo)

		self.docs = QPushButton()
		if self.docviewer.docs_ids and type(self.docviewer.docs_ids) == type([]) and len(self.docviewer.docs_ids) > 0:
			self.docs_pixmap = QPixmap( os.path.join('images', 'docs.jpg') )
		else:
			self.docs_pixmap = QPixmap( os.path.join('images', 'empty_folder.png') )		
		self.docs.setIcon(self.docs_pixmap)
		#self.docs.setAlignment(Qt.AlignCenter)
		self.docs.setIconSize(rect.size())
		self.docs.clicked.connect(self.show_docs)
		
		self.inb = QInvisibleButton(translate('Описание'))
		self.inb.setFont(self.font)
		self.desc = QTextEdit()
		if mode == 0:
			self.desc.setReadOnly(True)
		if 'desc' in people.keys():
			self.desc.setPlainText(people['desc'])

		layout.addWidget(self.photo, 0, 0, len(people.keys()), 1)
		layout.addWidget(self.docs, len(people.keys())+2, 0, 1, 1)
		layout.addWidget(self.desc, len(people.keys())+2, 1, 1, 1)
		layout.addWidget(self.inb, len(people.keys())+2, 1, 1, 1)
		#layout.addWidget(self.eventList, 0, 2, len(people.keys())+3, 1)

		i = 0
		for k, v in self.people.items():
		#	if mode == 0:
		#		if json_people.columns[i] == 'date_end' and str(e) == '':
		#			continue
		#		if json_people.columns[i] == 'maiden' and len(get_pol(data)) > 0 and get_pol(data)[0] == 'м':
		#			continue
			if k == 'desc':
				continue

			lb = QInvisibleButton(translate(k))
			lb.setFont(self.font)
			te = QLineEdit(str(v))
			te.setFont(self.font)
			te.setReadOnly(True)			
			self.buttext.append([lb, te])
			#if json_people.columns[i] == 'maiden' and len(get_pol(data)) > 0 and  get_pol(data)[0] == 'м':
			#	continue
			layout.addWidget(te, i, 1, 1, 1)
			layout.addWidget(lb, i, 1, 1, 1)
			if mode:
				te.setReadOnly(False)
				lb.clicked.connect(self.button_pressed)
				te.editingFinished.connect(self.line_edit_finished)
			i = i + 1
			
		if (mode == 1) or (mode == 2):
			bn = QPushButton('Сохранить')
			bn.setStyleSheet("font-weight: bold; font-size:11pt;")
			#bn.setFont(self.font)
			layout.addWidget(bn, len(people.keys())+3, 0, 1, 2)
			#layout.addWidget(bn, 1 , len(json_people.columns) + 1, 1, 1)
			bn.clicked.connect(self.save_press)
					

		self.setLayout(layout)

	def save_press(self):
		#sender = self.sender()		
		people = {}
		for e in self.buttext:
			people[translate(e[0].text())] = e[1].text()
		people['desc'] = self.desc.toPlainText()
		print(self.edit_people(people))
		self.db.peoples.save()
		self.close()
		

	def read_binary(self, filename):
		with open(filename, 'rb') as f:
			return f.read()

	def write_binary(self, filename, data):
		with open(filename, 'wb') as f:
			return f.write(data)

	def show_photo(self):
		if self.gallery:		
			self.gallery.exec_()
			if self.gallery.curpixmap:
				self.pixmap = QPixmap(self.gallery.curpixmap)				
			else:
				self.pixmap = QPixmap( os.path.join('images', 'f.png') )					
			self.change_icon()

	def show_docs(self):
		if self.docviewer:
			self.docviewer.exec_()
		if self.docviewer.docs_ids and type(self.docviewer.docs_ids) == type([]) and len(self.docviewer.docs_ids) > 0:
			self.docs_pixmap = QPixmap(os.path.join('images', 'docs.jpg'))
		else:
			self.docs_pixmap = QPixmap( os.path.join('images', 'empty_folder.png') )	
		self.docs.setIcon(self.docs_pixmap)		
		self.docs.setIconSize(rect.size())	

	def get_exchange_id(self):		
		for e in self.buttext:				
			if translate( e[0].text() ) == 'id':
				return e[1].text()
		return 0

	def change_icon(self):			
		self.photo.setIcon(self.pixmap.scaled(rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
		self.photo.setIconSize(rect.size())

	def photo_load(self):
		dialog = QFileDialog()
		fileNames = []
		if (dialog.exec()):
	  		fileNames = dialog.selectedFiles()
		if len(fileNames) > 0:
			self.photofile = fileNames[0]
			self.pixmap = QPixmap(self.photofile)
			self.change_icon()
			

	def button_pressed(self):
		sender = self.sender()
		for b, l in self.buttext:
			if sender == b:
				b.stackUnder(l)
				l.setFocus()

	def line_edit_finished(self):
		sender = self.sender()
		for b, l in self.buttext:
			if sender == l:
				l.stackUnder(b)
				b.setFocus()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	app.setStyle('Fusion')
    # Здесь будем работать со стилями(пока в разработке)
    #QApplication.setStyle(QStyleFactory.create("windowsvista"))
    
	db = AllTables('database/objects')
	people = db.get_people(1)
	p = PersonalCard(people, db, 1)
	p.show()

	sys.exit(app.exec_())