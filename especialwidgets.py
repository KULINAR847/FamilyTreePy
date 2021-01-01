from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from dictionary import translate
import copy
from treecard import TreeCard

class QInvisibleButton(QPushButton):
	def __init__(self, text='',parent = None):
		super().__init__(parent)
		self.setFlat(True)
		self.setText(text)
		self.setStyleSheet("* { background-color: rgba(255,255,255,100); color: rgba(0,0,0,100); text-align:right; }")

class QTextEditM(QTextEdit):
	focusOut = Signal()
	def __init__(self, text='', parent=None):
		super().__init__(parent)
		self.setPlainText(text)

	def focusOutEvent(self, event):
		self.focusOut.emit()
		return super().focusOutEvent(event)

class QLineEditM(QLineEdit):
	focusOut = Signal()
	def __init__(self, text='', parent=None):
		super().__init__(parent)
		self.setText(text)

	def focusOutEvent(self, event):
		self.focusOut.emit()
		return super().focusOutEvent(event)

class LineEditDesc(QWidget):
	def __init__(self, desc ='', text='', line_edit=True, mode=0, parent=None):
		super().__init__(parent)
		layout = QGridLayout()
		self.setLayout(layout)
		self.line_edit = line_edit
		if type(desc) == type([]) and len(desc) == 2:
			self.key = str(desc[0])
			desc = desc[1]
		elif type(desc) == type('') and desc != '':
			self.key = desc
		else:
			self.key = 0
		self.invButton = QInvisibleButton(desc)
		if line_edit:
			self.textWidget = QLineEditM(text)
		else:
			self.textWidget = QTextEditM(text)
		self.textWidget.setReadOnly(True)
		self.mutex = 0
				
		layout.addWidget(self.textWidget, 0, 0, 1, 1)
		layout.addWidget(self.invButton, 0, 0, 1, 1)

		if mode:						
			self.textWidget.setReadOnly(False)
			self.invButton.clicked.connect(self.button_pressed)
			self.textWidget.focusOut.connect(self.line_edit_finished)

	def get_text(self):
		if self.line_edit:
			return self.textWidget.text()
		else:
			return self.textWidget.toPlainText()

	def set_text(self, text):
		if self.line_edit:
			self.textWidget.setText(text)
		else:
			self.textWidget.setPlainText(text)

	def button_pressed(self):
		#print('button_pressed ' + str(self.key))
		self.invButton.stackUnder(self.textWidget)
		self.textWidget.setFocus()


	def line_edit_finished(self):
		#print('line_edit_finished')
		self.textWidget.stackUnder(self.invButton)
		self.invButton.setFocus()



class DictViewer(QWidget):
	def __init__(self, d={}, mode=0, invisible_fields=[], editable_fields=[], parent=None):
		super().__init__(parent)
		layout = QGridLayout()
		self.setLayout(layout)
		self.d = d
		self.d_bakup = copy.copy(d)		

		self.widgets = []
		
		i = 0
		for k, v in d.items():
			if k in invisible_fields:
				continue
			is_editable = k in editable_fields
			is_desc = not(k == 'desc' or k == 'event_desc') 
			w = LineEditDesc([str(k), translate(k)], str(v), is_desc, is_editable and mode)
			self.widgets.append(w)		
			
			layout.addWidget(w, i, 0, 1, 1)			
			i = i + 1

	def setValue(self, key, value):
		for w in self.widgets:
			if w.key == key:
				w.set_text(value)

	def get_changes(self):
		new_data = {}
		for w in self.widgets:
			k = w.key
			v = w.get_text()
			if type(self.d_bakup) == type({}):
				if k in self.d_bakup.keys():
					if str(self.d_bakup[k]) != str(v):
						new_data[k] = v
				else:
					new_data[k] = v
			else:
				print('bad type in DictViewer')
		return new_data

class RelStrings(QWidget):
	def __init__(self, record=0, db=0, mode=0, parent=None):
		super().__init__(parent)
		self.changed = False
		self.parent = parent
		#self.resize(600, self.height())

		self.pid = record['pid']
		self.ppid = record['ppid']
		self.record = record		
		self.db = db
		self.mode = mode
		self.pol = parent.pol

		self.relations = self.db.get_relations(self.pid)
		self.text = self.db.peoples.get_fio(self.ppid) if type(self.ppid) == type(0) else ''
		
		self.layout = QHBoxLayout()
		self.setLayout(self.layout)

		self.fill_data(self.record)


	def fill_data(self, data=0):
		print(data)
		self.combo = QComboBox()
		if type(self.pol) == type('') and len(self.pol) > 0:
			if self.pol[0].lower() == 'м':
				self.combo.addItems(['МАТЬ', 'ОТЕЦ', 'ЖЕНА', 'ПАРТНЕРША'])
			elif self.pol[0].lower() == 'ж':
				self.combo.addItems(['МАТЬ', 'ОТЕЦ', 'МУЖ', 'ПАРТНЕР'])
			else:
				self.combo.addItems(['МАТЬ', 'ОТЕЦ', 'МУЖ/ЖЕНА', 'ПАРТНЕР(ША)'])
		else:
			self.combo.addItems(['МАТЬ', 'ОТЕЦ', 'МУЖ/ЖЕНА', 'ПАРТНЕР(ША)'])
		
		if data:
			self.combo.setCurrentIndex(data['typeid']-1)

		self.combo.currentIndexChanged.connect(self.on_currentIndexChanged)

		
		self.lineEdit = QLineEdit(self.text)
		self.lineEdit.setReadOnly(True)
		#self.lineEdit.setGeometry(self.lineEdit.x(), self.lineEdit.y(), 800, self.lineEdit.height())
		self.button = QPushButton('...')
		self.button.clicked.connect(self.open_peoples_list)
		self.del_button = QPushButton('Удалить')
		self.del_button.clicked.connect(self.delete_record)				
		
		self.layout.addWidget(self.combo)
		self.layout.addWidget(self.lineEdit)
		self.layout.addWidget(self.button)
		self.layout.addWidget(self.del_button)

	def on_currentIndexChanged(self, index):
		rel_keys = sorted([typeid for typeid in self.relations.keys()]) if self.relations else []
		typeid = index + 1	
		print(typeid)
		if typeid in rel_keys:
			print('edit')
			self.db.edit_relation({'pid': self.pid, 'typeid': typeid})
		else:
			print('add')
			self.db.add_relation({'pid': self.pid, 'typeid': typeid})
			relations = self.db.get_relations(self.pid)
			print(relations)

	def open_peoples_list(self):
		button = self.sender()
		card = TreeCard(self.db)
		if card.exec_():
			self.lineEdit.setText( self.db.peoples.get_fio(card.pid) )	
			rel_keys = sorted([typeid for typeid in self.relations.keys()]) if self.relations else []
			typeid = self.combo.currentIndex() + 1	
			if typeid in rel_keys:
				print('edit')
				self.db.edit_relation({'pid': self.pid, 'typeid': typeid, 'ppid': card.pid})
			else:
				print('add')
				self.db.add_relation({'pid': self.pid, 'typeid': typeid, 'ppid': card.pid})
				relations = self.db.get_relations(self.pid)
				print(relations)

	def delete_record(self):		
		typeid = self.combo.currentIndex() + 1		
		if typeid >= 0:
			if self.db.del_relation({'pid': self.pid, 'typeid':typeid}):
				if self.parent is not None:
					self.parent.changed = True
				self.close()
		else:
			self.close()

		
class RelViewer(QWidget):
	def __init__(self, pid=0, db=0, mode=0, parent=None):
		super().__init__(parent)
		self.changed = False
		#self.resize(800, self.height())
		self.pid = pid
		self.db = db
		self.mode = mode

		self.backup_relations = copy.deepcopy(self.db.get_relations(self.pid))
		self.relations = self.db.get_relations(self.pid)

		self.pol = self.db.get_people(self.pid)['pol']

		self.layout = QVBoxLayout()
		self.setLayout(self.layout)	
		
		self.rel_widgets = []

		self.fill_relatives()
		

	def fill_relatives(self):
		rel_keys = sorted([typeid for typeid in self.relations.keys()])
		
		for key in rel_keys:
			record = self.relations[key]			
			w = RelStrings(record, self.db, self.mode, self)
			self.rel_widgets.append(w)
			self.layout.addWidget(w)

	def be_changed(self):		
		self.relations = self.db.get_relations(self.pid)
		print(self.relations)
		print(self.backup_relations)
		return self.backup_relations != self.relations


	def add_relative(self):
		record = self.db.relations.object	
		record['pid'] = self.pid	
		w = RelStrings(record, self.db, self.mode, self)
		self.rel_widgets.append(w)
		self.layout.addWidget(w)

		self.changed = True

	def update_backup(self):
		self.backup_relations = copy.deepcopy(self.db.get_relations(self.pid))


			



