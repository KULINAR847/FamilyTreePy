import sys
import copy
import os

from PySide2.QtWidgets import QApplication, QMainWindow, QGridLayout, QTableView, QWidget, QMenu, QAction, QTableWidget, QAbstractItemView, QLineEdit, QComboBox, QDialog, QMessageBox 
from PySide2.QtCore import QTranslator, QLibraryInfo, QAbstractTableModel, QModelIndex, Qt, QObject, QItemSelectionModel, Signal, QUrl, QSortFilterProxyModel, QTimer
from PySide2.QtGui import QStandardItemModel, QColor, QFont

from driver import AllTables
from personcard import PersonalCard, QInvisibleButton
from relationcard import RelationCard
from tablemodel import TableModel
from drawallgraph import GraphDrawer
from gallery_miniature import GalleryMiniature
from albumviewer import AlbumViewer

green = QColor(170,170,90)
blue  = QColor(70,180,180)
red   = QColor(180,70,180)

mainfont = QFont("Arial", 10)

class MyDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__()        

        self.resize(400,50)
        self.engine = 'dot'
        self.comboBox = QComboBox(self)
        self.engines = [('dot', 'for drawing directed graphs'),
            ('neato', 'for drawing undirected graphs'),
            ('twopi', 'for radial layouts of graphs'),
            ('circo', 'for circular layout of graphs'),
            ('fdp', 'for drawing undirected graphs'),
            ('sfdp', 'for drawing large undirected graphs'),
            ('patchwork', 'for squarified tree maps'),
            ('osage', 'for array-based layouts') ]
        for name, desc in self.engines:
            self.comboBox.addItem(name)

        self.comboBox.activated[str].connect(self.my_method)

    def my_method(self, engine_name):
        index = self.comboBox.currentIndex()
        self.setWindowTitle(self.engines[index][1])
        self.engine = engine_name
        print(self.engine)
        #return my_text

class TdisMainForm(QMainWindow):
    def __init__(self, parent = None):
        super().__init__()        
        self.setWindowTitle("Родословная")
        self.resize(800,self.height())
        self.distance = 1000

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)    
        
        layout = QGridLayout()        
        self.central_widget.setLayout(layout)

        self.lb_find = QInvisibleButton('Поиск')
        self.lb_find.setFont(mainfont)
        self.te_find = QLineEdit()
        self.te_find.setFont(mainfont)
               

        layout.addWidget(self.te_find, 0, 0, 1, 1)
        layout.addWidget(self.lb_find, 0, 0, 1, 1)
        #if mode:
         #   te.setReadOnly(False)
        self.lb_find.clicked.connect(self.button_pressed)
        self.te_find.returnPressed.connect(self.line_edit_return_pressed)
        
        

        self.table = QTableView()       # Создаём таблицу 
        self.table.doubleClicked.connect(self.viewPerson)   
        layout.addWidget(self.table)       
        self.table.setFocus()
        timer = QTimer(self)
        timer.singleShot(0, self.async_init)

    def async_init(self):
        self.database = AllTables('database/objects')

        self.model = TableModel(self.database.get_peoples())
        self.table.setModel(self.model)
        self.table.resizeRowsToContents()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.model.dataChanged.connect(self.table.update)

        # Работаем с выпадающим меню
        def openMenu(position):
            menu = QMenu()
            relAction = menu.addAction('Связи')
            menu.addSeparator()
            albAction = menu.addAction('Альбомы')
            menu.addSeparator()      
            miniatureAction = menu.addAction('Миниатюра')
            menu.addSeparator()                 
            viewAction = menu.addAction('Просмотреть') 
            addAction = menu.addAction('Добавить')
            editAction = menu.addAction('Редактировать')
            delAction = menu.addAction('Удалить')
            menu.addSeparator() 
            drawGraphAction = menu.addAction('Построить дерево')
            menu.addSeparator()  
            quitAction = menu.addAction('Выход')
            action = menu.exec_(self.table.mapToGlobal(position))
            
            if action == viewAction:
                self.viewPerson() 

            if action == miniatureAction:                
                p = self.get_selected_people()
                print('p = ' + str(p))
                if p is not None:
                    photo_ids = self.database.get_all_photo_ids(p['pid'])
                    path = 0
                    if photo_ids and type(photo_ids) == type([]) and len(photo_ids) > 0:
                        path = self.database.get_photo_path(p['pid'], photo_ids[0])
                    gm = GalleryMiniature(p['pid'], path)
                    gm.exec()
            
            if action == albAction:
                p = self.get_selected_people()
                if p is not None:
                    self.albuns = AlbumViewer(p['pid'], self.database, 1)
                    self.albuns.show()            

            if action == addAction:
                self.personal_card = PersonalCard(self.database.get_people(self.database.add_people({})), self.database, 1) 
                self.personal_card.exec_()

                self.line_edit_return_pressed()                      

            if action == editAction:
                p = self.get_selected_people()
                if p is not None:
                    self.personal_card = PersonalCard(p, self.database, 1) 
                    self.personal_card.exec_()

                    self.line_edit_return_pressed()

            if action == delAction:
                res = QMessageBox.question(self, 'ВНИМАНИЕ!!!', "Вы действительно хотите выполнить удаление?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if res == QMessageBox.Yes:
                    select = self.table.selectionModel()
                    if select.hasSelection():
                        id_list = [index.data() for index in self.table.selectionModel().selection().indexes() if index.column() == 0]   
                        print(id_list) 
                        self.database.del_people(id_list) 
                        self.database.peoples.save()
                        for pid in id_list:    
                            print('remove = ' + str(self.model.removeRow(pid)))  
                    
                    self.line_edit_return_pressed()                   

            if action == relAction:                
                pid = self.get_selected_pid()
                backup_relations = copy.deepcopy( self.database.relations )
                self.relation_card = RelationCard(pid, self.database, 2) 
                if not self.relation_card.exec_():
                    self.database.relations = backup_relations

            if action == drawGraphAction:
                print('draw graph')
                #dialog = MyDialog()
                #dialog.exec_()
                #engine = dialog.engine
                engine = 'dot'
                self.gd = GraphDrawer(self.database, engine)

            if action == quitAction:
                qApp.quit()  

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)          
        self.table.customContextMenuRequested.connect(openMenu)

    def get_selected_pid(self):
        pid_list = [index.data() for index in self.table.selectionModel().selection().indexes() if index.column() == 0]   
        if len(pid_list) == 1:
            return int(pid_list[0])
        return None

    def get_selected_people(self):
        pid_list = [index.data() for index in self.table.selectionModel().selection().indexes() if index.column() == 0]   
        if len(pid_list) == 1:
            return self.database.get_people(int(pid_list[0]))
        return None

    def viewPerson(self):
        p = self.get_selected_people()
        if p is not None:
            self.personal_card = PersonalCard(p, self.database, 0) 
            self.personal_card.show() 
    
    def button_pressed(self):
        self.lb_find.stackUnder(self.te_find)
        self.te_find.setFocus()

    def line_edit_return_pressed(self):
        print(self.te_find.text())

        self.model = TableModel(self.database.get_peoples())

        self.proxy_model = QSortFilterProxyModel(self.model)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterFixedString(self.te_find.text())
        self.proxy_model.setFilterKeyColumn(-1)
        
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
    
    # Получим строку подключения к БД
    connection = {}

    # Если всё хорошо запускаем приложение
    window = TdisMainForm(connection)
    window.show()
    sys.exit(app.exec_())
    
# Куда же без этих строк
if __name__ == '__main__':
    #write_log('==== Действия за [' + str(datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")) + '] ============\n','a')
    # Пожалуй самое главное в жизни этой программы
    main()