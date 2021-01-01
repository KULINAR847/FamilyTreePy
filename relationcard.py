import sys

from PySide2.QtWidgets import QDialog, QVBoxLayout, QPushButton, QMessageBox, QApplication
from PySide2.QtCore import QTranslator, QLibraryInfo
from PySide2.QtGui import QFont


from driver import AllTables
from treecard import TreeCard
from especialwidgets import RelViewer

mainfont = QFont("Arial", 10)

class RelationCard(QDialog):
	def __init__(self, pid=0, db=0, mode=0):
		super().__init__()

		self.resize(500,200)
		self.setFont(mainfont)

		self.pid = pid		
		self.db = db
		self.mode = mode
		
		self.layout = QVBoxLayout()	
		self.setLayout(self.layout)

		self.relations = self.db.get_relations(self.pid)
		self.relatives = RelViewer(self.pid, self.db, self.mode)
	
		self.bnAddRelative = QPushButton('Добавить')
		self.bnAddRelative.clicked.connect(self.addFieldsToLayout)
		self.layout.addWidget(self.bnAddRelative)

		self.layout.addWidget(self.relatives)

		self.bnSave = QPushButton('Сохранить')
		self.layout.addWidget(self.bnSave)
		self.bnSave.clicked.connect(self.save_press)

	
	def addFieldsToLayout(self, data=0):
		self.relatives.add_relative()

	def closeEvent(self, event):
		if self.relatives.be_changed():
			res = QMessageBox.question(self, 'ВНИМАНИЕ!!!', "Были зафиксированы изменения. Вы действительно хотите выйти без сохранения?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
			if res == QMessageBox.No:
				event.ignore()	

	def save_press(self):
		#sender = self.sender()
		if self.relatives.be_changed():
			print('Были изменения в связях')
			# if self.mode == 2:
			print('Они сохранены')
			self.db.relations.save()
			self.relatives.update_backup()
		self.accept()

def main():
	# app disexec теперь на pyqt
	app = QApplication(sys.argv)
	app.setStyle('Fusion')
	# Здесь будем работать со стилями(пока в разработке)
	#QApplication.setStyle(QStyleFactory.create("windowsvista"))
	
	# Русифицируем наше приложение
	translator = QTranslator()
	if (translator.load("qt_ru", QLibraryInfo.location(QLibraryInfo.TranslationsPath))):
		app.installTranslator(translator)

	# Если всё хорошо запускаем приложение
	db = AllTables('database/objects')
	window = RelationCard(4009, db, 2)
	window.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()