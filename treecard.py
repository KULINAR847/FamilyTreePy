import sys

from PySide2.QtWidgets import QApplication, QGridLayout, QTableView, QAbstractItemView, QLineEdit, QDialog 
from PySide2.QtCore import QTranslator, QLibraryInfo,  Qt, QSortFilterProxyModel
from PySide2.QtGui import QColor, QFont

from driver import AllTables
from tablemodel import TableModel
from personcard import QInvisibleButton


green = QColor(170,170,90)
blue  = QColor(70,180,180)
red   = QColor(180,70,180)

mainfont = QFont("Arial", 10)

class TreeCard(QDialog):
    def __init__(self, db=0, mode=0):
        super().__init__()

        layout = QGridLayout()        
        #self.central_widget.setLayout(layout)
        self.resize(800,self.height())
        self.lb_find = QInvisibleButton('Поиск')
        self.lb_find.setFont(mainfont)
        self.te_find = QLineEdit()
        self.te_find.setFont(mainfont)
        self.pid = 0       

        layout.addWidget(self.te_find, 0, 0, 1, 1)
        layout.addWidget(self.lb_find, 0, 0, 1, 1)
        #if mode:
         #   te.setReadOnly(False)
        self.lb_find.clicked.connect(self.button_pressed)
        self.te_find.returnPressed.connect(self.line_edit_return_pressed)
        
        self.database = db

        self.table = QTableView()       # Создаём таблицу 
        self.table.doubleClicked.connect(self.viewPerson)   
        #self.table = table

        self.model = TableModel(self.database.get_peoples())
        self.table.setModel(self.model)
        self.table.resizeRowsToContents()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        #self.table.setSelectionMode(QAbstractItemView.SingleSelection);
        self.model.dataChanged.connect(self.table.update)


        layout.addWidget(self.table)    
        self.setLayout(layout)

    def viewPerson(self):
        select = self.table.selectionModel()
        pid_list = [index.data() for index in self.table.selectionModel().selection().indexes() if index.column() == 0]   
        if len(pid_list) == 1:
            self.pid = int(pid_list[0])
            print(int(pid_list[0]))
            self.accept()
        return 0

    def button_pressed(self):
        #sender = self.sender()
        self.lb_find.stackUnder(self.te_find)
        self.te_find.setFocus()

    def line_edit_return_pressed(self):
        print(self.te_find.text())

        self.model = TableModel(self.database.get_peoples())

        self.proxy_model = QSortFilterProxyModel(self.model)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterFixedString(self.te_find.text())
        self.proxy_model.setFilterKeyColumn(-1)
        #print(self.proxy_model.filterKeyColumn())
        
        self.table.setModel(self.proxy_model) 
        self.table.update()   
        self.table.resizeRowsToContents() 

        #sender = self.sender()
        self.te_find.stackUnder(self.lb_find)
        self.lb_find.setFocus()
    

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
    window = TreeCard(AllTables('database/objects'), 0)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()