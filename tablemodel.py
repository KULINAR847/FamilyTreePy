from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt
from dictionary import translate

#class TableModel(QAbstractTableModel):
class TableModel(QAbstractTableModel):
    #dataChanged = Signal() 
    def __init__(self, table = {}):
        super().__init__()  
        self.tableDB = table
        self.rows = 0
        self.columns = self.tableDB.columns
        self.view_data = self.tableDB.rows
        self.rows_names = list(self.view_data.keys())
        #self.setHorizontalHeaderLabels(self.cols_names) 
        print(self.rows_names)        
        self.rows = len(self.view_data.keys())
        if self.rows > 0:
            for key_up in self.view_data.keys():
                for i, key in enumerate(self.view_data[key_up].keys()):
                    #print(key)
                    self.setHeaderData(i, Qt.Horizontal, key )
                self.columns_names = list(self.view_data[key_up].keys())
                if type(self.columns_names) == type([]) and 'desc' in self.columns_names:
                    self.columns_names.remove('desc')
                break
            
            print(self.columns_names)
            self.columns = len(self.columns_names)


    def rowCount(self, index):
        return self.rows

    def columnCount(self, index):
        if self.rows:
            return self.columns
        return 0

    def removeRow(self, row, parent = QModelIndex()):      
        print(row)
        if row in self.view_data.keys():
            del self.view_data[row]
            self.rows = len(self.view_data.keys())
            self.rows_names = list(self.view_data.keys())
            #self.set
            #self.dataChanged()
            return True        
        return False

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return translate(self.columns_names[section]) #('Font family') if section == 0 else ('Embedded')
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            #print(self.rows_names[ index.row() ])
            #print(self.columns_names[ index.column() ])
            #print('##########')
            return self.view_data[ self.rows_names[ index.row() ] ][ self.columns_names[ index.column() ] ]
