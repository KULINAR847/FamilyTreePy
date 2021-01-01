import pickle
import os
import copy
import shutil
import json
import datetime

# Parents
MOTHER = 1
FATHER = 2
STEPMOTHER = 3
STEPFATHER = 4

# Partners
PARTNER = 5

class DriverDB:
	def __init__(self, db_local_path ='', db_name='', data = {}):
		# db_path is list like ['database', 'hd5'] -> database\hd5 in windows
		self.cur_path = os.getcwd().replace('\\', '/').split(r'/')
		self.db_path = db_local_path.replace('\\', '/').split(r'/')
		self.db_name = db_name
		self.rows = data
		self.extension = '.mydb'
		self.columns = []

		self.create_file()

	def check_path_or_create(self):
		filepath = self.get_without_file_abspath()
		if not os.path.exists( filepath ):
			os.makedirs(filepath)
		return os.path.exists( self.get_with_file_abspath() )

	def get_without_file_abspath(self):		
		full_filepath = self.cur_path + self.db_path
		res = os.path.join( *full_filepath ).replace(':', ':\\')
		return str( res.replace(':', ':\\') if ':' in res else '/' + res )

	def get_with_file_abspath(self):		
		full_filepath = self.cur_path + self.db_path + [self.db_name + self.extension]
		res = os.path.join( *full_filepath ).replace(':', ':\\')
		return str( res.replace(':', ':\\') if ':' in res else '/' + res )

	def create_file(self):		
		if not self.check_path_or_create():
			self.save()

	def save(self):
		self.check_path_or_create()
		with open( self.get_with_file_abspath(), 'wb') as f:
			pickle.dump(self.rows, f)

	def read_rows(self):
		rows = {}
		if self.check_path_or_create():
			with open( self.get_with_file_abspath(), 'rb') as f:
				rows = pickle.load(f)
		else:
			print('No such file - ' + self.get_with_file_abspath())
		return rows

	# размер словаря
	def size(self):
		return len(self.rows.keys())

class TableDB(DriverDB):
	def __init__(self, db_local_path ='', db_name='', read_now = True):
		super().__init__(db_local_path, db_name)		
		self.object = {}
		self.columns = []
		self.rows = {}
		self.pkey = ''

	def get_next_id(self):		
		if type(self.rows) == type({}):			
			return max([0] + [int(key) for key in self.rows.keys()]) + 1
		return max([0]) + 1

	def add_object(self, row):
		new_object = copy.copy(self.object)	
		if self.pkey != '' and type(new_object) == type({}) and type(row) == type({}):			
			new_object.update(row)
			if self.pkey not in row.keys():
				new_object[self.pkey] = int(self.get_next_id())
			self.rows[int(new_object[self.pkey])] = new_object
			#self.save()
			return new_object[self.pkey]
		return False

	def edit_object(self, oid, row):
		if int(oid) in self.rows.keys():
			edit_object = self.rows[int(oid)]
			if self.pkey != '' and type(edit_object) == type({}) and type(row) == type({}):
				edit_object.update(row)
				if edit_object[self.pkey] == int(oid):
					self.rows[edit_object[self.pkey]] = edit_object
					#self.save()
					return True
		else:
			print('No such key!!!!!!')
		return False

	def del_object(self, oid):
		if int(oid) in self.rows.keys():
			del self.rows[int(oid)]
			#self.save()
			return True
		else:
			print('No such key!!!!!!')
		return False

class ListDB(DriverDB):
	def __init__(self, db_local_path ='', db_name='', read_now = True):
		super().__init__(db_local_path, db_name)		
		self.object = {}
		self.rows = {}
		self.pkey = ''
		self.lkey = ''

	def get_next_id(self, oid):	
		if type(self.rows) == type({}) and type(self.rows[int(oid)]) == type({}):			
			return max([0] + [int(k) for k in self.rows[int(oid)].keys()]) + 1
		return max([0]) + 1

	def add_object(self, row):
		new_object = copy.copy(self.object)	
		if self.pkey in row.keys():
			oid = int(row[self.pkey])
		else:
			oid = None
		if self.lkey in row.keys():
			lid = int(row[self.lkey])
		else:
			lid = None	
		if type(oid) == type(0) and type(new_object) == type({}) and type(row) == type({}):
			new_object.update(row)
			if int(oid) in self.rows.keys():
				if type(self.rows[int(oid)]) != type({}):
					print('В ListDB не словарь')
					return False
				new_object[self.pkey] = int(oid)
				if lid is None:
					new_object[self.lkey] = self.get_next_id(oid)
				else:
					if int(lid) in self.rows[int(oid)].keys():
						print('Такая запись уже существует!')
						return False
					new_object[self.lkey] = int(lid)
				self.rows[int(oid)][new_object[self.lkey]] = new_object
				#self.save()
				return new_object #[self.lkey] # True
			else:
				self.rows[int(oid)] = {}
				new_object[self.pkey] = int(oid)
				if lid is None:
					new_object[self.lkey] = 1
				else:
					new_object[self.lkey] = int(lid)
				self.rows[new_object[self.pkey]][new_object[self.lkey]] = new_object
				#self.save()
				return new_object #[self.lkey] # True
		return False

	def edit_object(self, row):
		if self.pkey in row.keys():
			oid = int(row[self.pkey])
		else:
			oid = None
		if self.lkey in row.keys():
			lid = int(row[self.lkey])
		else:			
			lid = None
		if type(oid) == type(0) and int(oid) in self.rows.keys():
			edit_dict = self.rows[int(oid)]
			edit_object = 0
			if type(lid) == type(0) and int(lid) in edit_dict.keys():
				edit_object = edit_dict[int(lid)]
			else:
				print('Нет такого lid')
				return False

			if self.pkey != '' and type(edit_object) == type({}) and type(row) == type({}):
				edit_object.update(row)
				edit_object[self.pkey] = int(edit_object[self.pkey])
				edit_object[self.lkey] = int(edit_object[self.lkey])
				#edit_object[]
				if edit_object[self.pkey] == int(oid) and edit_object[self.lkey] == int(lid):
					self.rows[edit_object[self.pkey]][edit_object[self.lkey]] = edit_object
					#self.save()
					return edit_object
			else:
				print('lid or pid is string')
		else:
			print('No such key!!!!!!')
		return False

	def del_object(self, oid):
		if int(oid) in self.rows.keys():
			del self.rows[int(oid)]
			#self.save()
			return True
		else:
			print('No such key!!!!!!')
		return False

	def del_list_record(self, oid, lid):
		if int(oid) in self.rows.keys() and int(lid) in self.rows[int(oid)].keys():			
			backup = copy.copy(self.rows[int(oid)][int(lid)])
			del self.rows[int(oid)][int(lid)]
			#self.save()
			return backup
		else:
			print('No such key!!!!!!')
		return False

class Peoples(TableDB):
	def __init__(self, db_local_path ='', db_name='', read_now = True):	
		super().__init__(db_local_path, db_name)			
		self.object = {'pid': 0, 'rid': '', 'name': '', 'surname': '',
						'maiden':'', 'midname': '', 'birthday': '', 'deathday': '', 'pol': '', 'photo_id': '', 'desc': ''}
		
		self.columns = list(self.object.keys())
		self.rows = self.read_rows() # read {} of data
		self.pkey = 'pid'

	def __str__(self):
		return 'To show all peoples use rows variable like print(peoples.rows)'

	def get_fio(self, pid, sep = ' ', with_maiden = False):
		pid = int(pid)
		if pid in self.rows.keys():
			surname = str(self.rows[pid]['surname']) if 'surname' in self.columns else ''
			name = str(self.rows[pid]['name']) if 'name' in self.columns else ''
			middle = str(self.rows[pid]['middle']) if 'middle' in self.columns else ''
			return surname + str(sep) + str('(' + str(self.rows[pid]['maiden']) + ')' + str(sep) if with_maiden and 'maiden' in self.columns and self.rows[pid]['maiden'] else '') + name + str(sep) + middle
		return 'Нет такого человека в базе'

	def add_description(self, pid, text):
		pid = int(pid)
		if pid in self.rows.keys():
			self.rows[pid]['desc'] = text

	def __repr__(self):
		return self.rows

class Events(ListDB):
	def __init__(self, db_local_path ='', db_name='', read_now = True):	
		super().__init__(db_local_path, db_name)			
		self.object = {'alid': 0, 'eid': 0, 'event_head': '', 'event_desc': '', 'event_date': '',
						'place': '', 'person_years': '', 'photo_ids': []}		
		
		self.rows = self.read_rows() # read {} of data
		self.pkey = 'alid'
		self.lkey = 'eid'
		self.nkeys = len(self.object.keys())		
		self.invizible_fields = [self.pkey, self.lkey, 'photo_ids']
		self.editable_fields = [key for key in self.object.keys() if key not in self.invizible_fields and key != 'event_head']

	def __repr__(self):
		res = ''
		for k, v in self.rows.items():
			res = res + str(k) + ' : ' + str(v) + '\n'
		return res

class Relations(ListDB):
	def __init__(self, db_local_path ='', db_name='', read_now = True):
		super().__init__(db_local_path, db_name)			
		self.object = {'pid': 0, 'typeid': 0, 'ppid': ''}
		
		self.columns = list(self.object.keys())
		self.rows = self.read_rows() # read {} of data
		self.pkey = 'pid'
		self.lkey = 'typeid'
		

	def get_pair(self, oid):
		mid, fid = 0, 0
		if int(oid) in self.rows[int(oid)]:
			if MOTHER in self.rows[int(oid)].keys():
				mid = self.rows[int(oid)][MOTHER]
			if FATHER in self.rows[int(oid)].keys():
				fid = self.rows[int(oid)][FATHER]
		return mid, fid

	def __repr__(self):
		return str(self.rows)

class AlbRelations(ListDB):
	def __init__(self, db_local_path ='', db_name='', read_now = True):
		super().__init__(db_local_path, db_name)			
		self.object = {'pid': 0, 'alid': 0}
		
		self.columns = list(self.object.keys())
		self.rows = self.read_rows() # read {} of data
		self.pkey = 'pid'
		self.lkey = 'alid'

	def __repr__(self):
		return str(self.rows)

class Files:
	def __init__(self, db_local_path = '', folder = 'tmp'):				
		if db_local_path != '':
			self.db_path = db_local_path.replace('\\', '/').split(r'/')			
			self.folder = folder.replace('\\', '/').split(r'/')
			path = self.db_path + self.folder			
			self.file_storage = os.path.join(*path)
		else:
			self.db_path = ''
			self.folder = folder.replace('\\', '/').split(r'/')			
			self.file_storage = os.path.join(*self.folder)		

		if not os.path.exists( self.file_storage ):
			os.makedirs(self.file_storage)

		#print(self.file_storage)
		self.objects = os.listdir(self.file_storage)
		#print(self.objects)

	def get_files_by_id(self, pid):
		files_dir = os.path.join(self.file_storage, str(pid))
		#print(files_dir)
		if os.path.exists( files_dir ):
			return [ os.path.join(files_dir, e) for e in os.listdir( files_dir ) ]
		else:
			return 0
	
	def save_file_by_id(self, pid, src, filename, rewrite=False):
		files_dir = os.path.join(self.file_storage, str(pid))
		files = []
		if not os.path.exists( files_dir ):
			os.makedirs(files_dir)
		else:
			files = os.listdir( files_dir )
		if filename not in files or rewrite:
			print('copy')
			shutil.copy2( src, os.path.join(files_dir, filename)) 
		else:
			print('Такой файл уже существует')

	def copy_file(self, src, dst):
		if os.path.exists( src ):
			shutil.copy2( src, dst )

	def del_file_by_id(self, pid, filename):
		files_dir = os.path.join(self.file_storage, str(pid))
		files = []
		if not os.path.exists( files_dir ):
			print('Такой директории не существует')
		else:
			files = os.listdir( files_dir )
		if filename in files:
			print(os.path.join(files_dir, filename))
			os.remove(os.path.join(files_dir, filename))
			#shutil.copy2( src, os.path.join(files_dir, filename)) 
		else:
			print('Такого файла уже не существует')
	
	def del_folder_by_id(self, pid):
		files_dir = os.path.join(self.file_storage, str(pid))
		if not os.path.exists( files_dir ):
			print('Такой директории не существует')
		else:
			shutil.rmtree(files_dir)
	
	def get_path_to_file(self, pid, filename):
		files_dir = os.path.join(self.file_storage, str(pid))
		filepath = os.path.join(files_dir, filename)
		#print(filepath)
		if os.path.exists(filepath):
			return filepath
		return 0

	def __repr__(self):
		return os.listdir( self.file_storage )

class Photos(ListDB):
	def __init__(self, db_local_path ='', db_name='', read_now = True):	
		super().__init__(db_local_path, db_name)			
		self.object = {'pid': 0, 'phid': 0, 'filename': '', 'oldpath': '', 'data': 0, 'eid': '',
						'place': '', 'person_years': '', 'photo_id': '', 'date' : '', 'dateadd' : ''}		
		
		self.rows = self.read_rows() # read {} of data
		self.pkey = 'pid'
		self.lkey = 'phid'
		self.datakey = 'data'
		self.files_manager = Files('/'.join(self.db_path), 'photos')

		#self.files_path = '/'.join(self.db_path), 'photos/' + str(self.pid)
		#self.files_manager = Files(self.files_path)
		#self.files = self.files_manager.get_files_by_id(self.pid)

	def get_files_by_id(self, oid):				
		list_files_with_dirs = self.files_manager.get_files_by_id(oid)
		list_files = list(map(os.path.basename, list_files_with_dirs))
		#if type(self.rows) == type({}) and int(oid) in self.rows.keys():
		#	if type(self.rows[int(oid)]) == type({}): #'data' in self.rows.keys():
				#records = self.rows[int(oid)]
				#print(list_files)
				#	if records[key]['filenumber']
		#		pass
		return list_files
		#return 0

	def __repr__(self):
		res = ''
		for k, v in self.rows.items():
			res = res + str(k) + ' : ' + str(v) + '\n'
		return res

class Docs(ListDB):
	def __init__(self, db_local_path ='', db_name='', read_now = True):	
		super().__init__(db_local_path, db_name)			
		self.object = {'pid': 0, 'did': 0, 'filename': '', 'oldpath': '', 'data': 0, 'eid': '',
						'place': '', 'person_years': '', 'photo_id': '', 'date' : '', 'desc': ''}		
		
		self.rows = self.read_rows() # read {} of data
		self.pkey = 'pid'
		self.lkey = 'did'
		self.files_manager = Files('/'.join(self.db_path), 'docs')

	def __repr__(self):
		res = ''
		for k, v in self.rows.items():
			res = res + str(k) + ' : ' + str(v) + '\n'
		return res

class Albums(ListDB):
	def __init__(self, db_local_path ='', db_name='', read_now = True):	
		super().__init__(db_local_path, db_name)			
		self.object = {'alid': 0, 'imid': 0, 'title': '', 'filename': '', 'oldpath': '', 'date' : '', 'desc': '', 'pids': 0}		
		
		self.rows = self.read_rows() # read {} of data
		self.pkey = 'alid'
		self.lkey = 'imid'
		self.files_manager = Files('/'.join(self.db_path), 'albums')
		self.invizible_fields = [self.pkey, self.lkey, 'filename', 'oldpath', 'pids']
		self.editable_fields = [key for key in self.object.keys() if key not in self.invizible_fields and key != 'title']

	def __repr__(self):
		res = ''
		for k, v in self.rows.items():
			res = res + str(k) + ' : ' + str(v) + '\n'
		return res

class AllTables:
	def __init__(self, db_local_path ='', read_now = True):
		self.peoples = Peoples(db_local_path, 'peoples')		
		self.relations = Relations(db_local_path, 'relations')
		self.events = Events(db_local_path, 'events')
		self.docs = Docs(db_local_path, 'docs')
		self.photos = Photos(db_local_path, 'photos')
		self.albums = Albums(db_local_path, 'albums')
		#self.albumsrel = AlbRelations(db_local_path, 'albumsrel')
			

	def add_people(self, people_data):
		if type(people_data) == type({}):
			return self.peoples.add_object(people_data)
		elif type(people_data) == type([]):
			for p in people_data:
				self.peoples.add_object(p)
		else:
			print('тип people_data при добавлении задан некорректно - ' + type(people_data))
		return False
		#self.peoples.save()
	
	def edit_people(self, people_data):
		if type(people_data) == type({}) and 'pid' in people_data.keys():
			pid = int(people_data['pid'])
			self.peoples.edit_object(pid, people_data)
			#self.peoples.save()
			return True
		return False

	def del_people(self, pid):		
		if type(pid) == type(1):
			self.peoples.del_object(int(pid))
		elif type(pid) == type([]):
			for p in pid:
				self.del_people(int(p))
		else:
			print('тип pid при удалении задан некорректно - ' + type(pid))
			return
		#self.peoples.save()

	def get_people(self, pid):
		if pid in self.peoples.rows.keys():
			return self.peoples.rows[pid]
		else:
			print('Нет такого pid = ' + str(pid))
			return 0

	def get_peoples(self, filter_peoples=0):
		if filter_peoples:
			return ''

		return self.peoples

	def add_relation(self, relation_data):
		res = []
		if type(relation_data) == type({}):
			res.append( self.relations.add_object(relation_data) )
		elif type(relation_data) == type([]):
			for p in relation_data:
				res.append( self.relations.add_object(p) )
		else:
			print('тип photo_data при добавлении задан некорректно - ' + type(relation_data))
		#self.photos.save()
		return res

	def get_relations(self, pid=0):		
		if pid:
			if pid in self.relations.rows.keys():
				return self.relations.rows[pid]
		return 0

	def edit_relation(self, relation_data):
		if type(relation_data) == type({}) and self.relations.pkey in relation_data.keys() and self.relations.lkey in relation_data.keys():			
			self.relations.edit_object(relation_data)
			#self.photos.save()
			return True
		return False

	def del_relation(self, relation_data):
		if type(relation_data) == type({}) and self.relations.pkey in relation_data.keys() and self.relations.lkey in relation_data.keys():
			pid = int(relation_data[self.relations.pkey])	
			lid = int(relation_data[self.relations.lkey])		
			if self.relations.del_list_record(pid, lid):
				print('Запись успешно удалена - ' + str(pid))
				#self.photos.save()
				return True
			else:
				print('Запись не удалена - ' + str(pid))
		return False

	def add_photo(self, photo_data):
		res = []
		if type(photo_data) == type({}):
			if 'oldpath' in photo_data.keys() and photo_data['oldpath']	!= '':	
				if os.path.exists(photo_data['oldpath']):
					_, ext = os.path.splitext(photo_data['oldpath'])
					photo_data = self.photos.add_object(photo_data)
					photo_data['filename'] = str(photo_data[self.photos.lkey]) + ext
					res.append( self.photos.edit_object(photo_data) )					
					if res[0]:						
						self.photos.files_manager.save_file_by_id(photo_data['pid'], photo_data['oldpath'], photo_data['filename'])
				else:
					print('Такого файла' + str(photo_data['oldpath']) + 'не существует!')
		elif type(photo_data) == type([]):
			for p in photo_data:
				if 'oldpath' in p.keys() and p['oldpath'] != '':
					if os.path.exists(p['oldpath']):
						_, ext = os.path.splitext(p['oldpath'])
						p = self.photos.add_object(p)
						p['filename'] = str(p[self.photos.lkey]) + ext
						res.append( self.photos.edit_object(p) )					
						if res[len(res)-1]:						
							self.photos.files_manager.save_file_by_id(p['pid'], p['oldpath'], photo_data['filename'])
		else:
			print('тип photo_data при добавлении задан некорректно - ' + type(photo_data))
		self.photos.save()
		return res
	
	def edit_photo(self, photo_data):
		if type(photo_data) == type({}) and self.photos.pkey in photo_data.keys() and self.photos.lkey in photo_data.keys():		
			if 'oldpath' in photo_data.keys() and photo_data['oldpath']	!= '':
				if os.path.exists(photo_data['oldpath']):
					data = self.get_photo_data(photo_data[self.photos.pkey], photo_data[self.photos.lkey])
					if type(data) == type({}) and 'filename' in data.keys() and data['filename'] != '':
						self.photos.files_manager.del_file_by_id(photo_data[self.photos.pkey], data['filename'])
					_, ext = os.path.splitext(photo_data['oldpath'])
					photo_data['filename'] = str(photo_data[self.photos.lkey]) + ext
					res = self.photos.edit_object(photo_data)				
					if res:						
						self.photos.files_manager.save_file_by_id(photo_data['pid'], photo_data['oldpath'], photo_data['filename'], True)
						self.photos.save()
						return True
				else:
					print('Нет такого файла ' + str(photo_data['oldpath']))
			else:
				# Просто отредактируем параметры
				if self.photos.edit_object(photo_data):
					self.photos.save()
					return True
		else:
			print('Нет задан один из параметров pid или phid')
			
		return False

	def del_photo(self, photo_data):
		if type(photo_data) == type({}) and self.photos.pkey in photo_data.keys() and self.photos.lkey in photo_data.keys():
			pid = int(photo_data[self.photos.pkey])	
			lid = int(photo_data[self.photos.lkey])	
			photo_data = self.photos.del_list_record(pid, lid)	
			if photo_data:
				self.photos.files_manager.del_file_by_id(pid, photo_data['filename'])
				print('Запись успешно удалена - ' + str(pid))
				self.photos.save()
				return True
			else:
				print('Запись не удалена - ' + str(pid))
		return False
		

	def del_all_photo(self, pid):		
		if type(pid) == type(1):
			self.photos.del_object(int(pid))
			self.photos.files_manager.del_folder_by_id(pid)
			self.photos.save()
		elif type(pid) == type([]):
			for p in pid:
				self.del_all_photo(int(p))
		else:
			print('тип pid при удалении задан некорректно - ' + type(pid))
			return False
		#self.photos.save()
		return True

	def get_photo_data(self, pid, phid):	
		rows = self.photos.rows
		if type(rows) == type({}) and int(pid) in rows.keys() and int(phid) in rows[int(pid)].keys() and 'filename' in rows[int(pid)][int(phid)].keys():
			return rows[int(pid)][int(phid)]
		return 0

	def get_photo_path(self, pid, phid):	
		rows = self.photos.rows
		if type(rows) == type({}) and int(pid) in rows.keys() and int(phid) in rows[int(pid)].keys() and 'filename' in rows[int(pid)][int(phid)].keys():
			return self.photos.files_manager.get_path_to_file(pid, rows[int(pid)][int(phid)]['filename'])
		return 0

	def get_all_photo_ids(self, pid):
		rows = self.photos.rows
		if type(rows) == type({}) and int(pid) in rows.keys():
			return list(rows[int(pid)].keys())
		return 0

	def add_doc(self, doc_data):
		res = []
		data = doc_data
		objects = self.docs
		pkey = objects.pkey
		if type(data) == type({}):
			if 'oldpath' in data.keys() and data['oldpath']	!= '':	
				if os.path.exists(data['oldpath']):
					_, ext = os.path.splitext(data['oldpath'])
					data = objects.add_object(data)
					data['filename'] = str(data[objects.lkey]) + ext
					res.append( objects.edit_object(data) )					
					if res[0]:						
						objects.files_manager.save_file_by_id(data[pkey], data['oldpath'], data['filename'])
				else:
					print('Такого файла' + str(data['oldpath']) + 'не существует!')
		elif type(data) == type([]):
			for p in data:
				if 'oldpath' in p.keys() and p['oldpath'] != '':
					if os.path.exists(p['oldpath']):
						_, ext = os.path.splitext(p['oldpath'])
						p = objects.add_object(p)
						p['filename'] = str(p[objects.lkey]) + ext
						res.append( objects.edit_object(p) )					
						if res[len(res)-1]:						
							objects.files_manager.save_file_by_id(p[pkey], p['oldpath'], data['filename'])
		else:
			print('тип photo_data при добавлении задан некорректно - ' + type(data))
		self.docs.save()
		return res

	def edit_doc(self, doc_data):
		data = doc_data
		objects = self.docs
		if type(data) == type({}) and objects.pkey in data.keys() and objects.lkey in data.keys():		
			if 'oldpath' in data.keys() and data['oldpath']	!= '':
				if os.path.exists(data['oldpath']):
					data_old = self.get_doc_data(data[objects.pkey], data[objects.lkey])
					if type(data_old) == type({}) and 'filename' in data_old.keys() and data_old['filename'] != '':
						objects.files_manager.del_file_by_id(data_old[objects.pkey], data_old['filename'])
					_, ext = os.path.splitext(data['oldpath'])
					data['filename'] = str(data[objects.lkey]) + ext
					for k in data_old.keys():
						if k not in data.keys():
							data[k] = data_old[k]
					res = objects.edit_object(data)			
					if res:						
						objects.files_manager.save_file_by_id(data['pid'], data['oldpath'], data['filename'], True)
						objects.save()
						return True
				else:
					print('Нет такого файла ' + str(data['oldpath']))
			else:
				# Просто отредактируем параметры
				if objects.edit_object(data):
					objects.save()
					return True
		else:
			print('Не задан один из параметров pid или phid')			
		return False

	def del_doc(self, doc_data):
		data = doc_data
		objects = self.docs
		if type(data) == type({}) and objects.pkey in data.keys() and objects.lkey in data.keys():
			pid = int(data[objects.pkey])	
			lid = int(data[objects.lkey])	
			data_del = objects.del_list_record(pid, lid)	
			if data_del:
				objects.files_manager.del_file_by_id(pid, data_del['filename'])
				print('Запись успешно удалена - ' + str(pid))
				objects.save()
				return True
			else:
				print('Запись не удалена - ' + str(pid))
		return False

	def del_all_docs(self, pid):
		objects = self.docs	
		if type(pid) == type(1):
			objects.del_object(int(pid))
			objects.files_manager.del_folder_by_id(pid)
			objects.save()
		elif type(pid) == type([]):
			for p in pid:
				self.del_all_docs(int(p))
		else:
			print('тип pid при удалении задан некорректно - ' + str(type(pid)))
			return False
		#self.photos.save()
		return True

	def save_doc(self, src, dst):
		objects = self.docs	
		if not os.path.exists(dst):			
			objects.files_manager.copy_file(src, dst)	
		else:
			print('Такой путь уже существует - ' + str(dst))
			return False
		#self.photos.save()
		return True

	def get_doc_data(self, pid, phid):	
		rows = self.docs.rows
		if type(rows) == type({}) and int(pid) in rows.keys() and int(phid) in rows[int(pid)].keys() and 'filename' in rows[int(pid)][int(phid)].keys():
			return rows[int(pid)][int(phid)]
		return 0

	def get_doc_path(self, pid, phid):	
		rows = self.docs.rows
		objects = self.docs
		if type(rows) == type({}) and int(pid) in rows.keys() and int(phid) in rows[int(pid)].keys() and 'filename' in rows[int(pid)][int(phid)].keys():
			return objects.files_manager.get_path_to_file(pid, rows[int(pid)][int(phid)]['filename'])
		return 0

	def get_all_doc_ids(self, pid):
		rows = self.docs.rows
		if type(rows) == type({}) and int(pid) in rows.keys():
			return list(rows[int(pid)].keys())
		return 0


	#### ALBUMS ######
	def add_album(self, album_data):
		res = []
		data = album_data
		pkey = self.albums.pkey
		objects = self.albums
		if type(data) == type({}):
			if pkey not in data.keys():
				data[pkey] = len(objects.rows)+1
			if 'oldpath' in data.keys() and data['oldpath']	!= '':	
				if os.path.exists(data['oldpath']):
					_, ext = os.path.splitext(data['oldpath'])
					data = objects.add_object(data)
					data['filename'] = str(data[objects.lkey]) + ext
					res.append( objects.edit_object(data) )					
					if res[0]:						
						objects.files_manager.save_file_by_id(data[pkey], data['oldpath'], data['filename'])
				else:
					print('Такого файла' + str(data['oldpath']) + 'не существует!')
			else:
				print(data)
				res.append( objects.add_object(data) )
		elif type(data) == type([]):
			for p in data:
				if pkey not in p.keys():
					p[pkey] = len(objects.rows)+1
				if 'oldpath' in p.keys() and p['oldpath'] != '':
					if os.path.exists(p['oldpath']):
						_, ext = os.path.splitext(p['oldpath'])
						p = objects.add_object(p)
						p['filename'] = str(p[objects.lkey]) + ext
						res.append( objects.edit_object(p) )					
						if res[len(res)-1]:						
							objects.files_manager.save_file_by_id(p[pkey], p['oldpath'], data['filename'])
				#self.albums.save()
		else:
			print('тип photo_data при добавлении задан некорректно - ' + type(data))
		self.albums.save()
		return res

	def edit_album(self, album_data):
		data = album_data
		objects = self.albums
		pkey = self.albums.pkey
		if type(data) == type({}) and objects.pkey in data.keys() and objects.lkey in data.keys():		
			if 'oldpath' in data.keys() and data['oldpath']	!= '':
				if os.path.exists(data['oldpath']):
					data_old = self.get_doc_data(data[objects.pkey], data[objects.lkey])
					if type(data_old) == type({}) and 'filename' in data_old.keys() and data_old['filename'] != '':
						objects.files_manager.del_file_by_id(data_old[objects.pkey], data_old['filename'])
					_, ext = os.path.splitext(data['oldpath'])
					data['filename'] = str(data[objects.lkey]) + ext
					for k in data_old.keys():
						if k not in data.keys():
							data[k] = data_old[k]
					res = objects.edit_object(data)			
					if res:						
						objects.files_manager.save_file_by_id(data[pkey], data['oldpath'], data['filename'], True)
						objects.save()
						return data
				else:
					print('Нет такого файла ' + str(data['oldpath']))
			else:
				# Просто отредактируем параметры
				if objects.edit_object(data):
					objects.save()
					return data
		else:
			print('Не задан один из параметров pid или phid')			
		return False

	def del_photo_from_album(self, album_data):
		data = album_data
		objects = self.albums
		if type(data) == type({}) and objects.pkey in data.keys() and objects.lkey in data.keys():
			pid = int(data[objects.pkey])	
			lid = int(data[objects.lkey])	
			data_del = objects.del_list_record(pid, lid)	
			if data_del:
				objects.files_manager.del_file_by_id(pid, data_del['filename'])
				print('Запись успешно удалена - ' + str(pid))
				objects.save()
				return True
			else:
				print('Запись не удалена - ' + str(pid))
		return False

	def del_album(self, alid):
		objects = self.albums			
		if type(alid) == type(1):
			objects.del_object(int(alid))
			objects.files_manager.del_folder_by_id(alid)
			objects.save()
		elif type(alid) == type([]):
			for p in alid:
				self.del_album(int(p))
		else:
			print('тип alid при удалении задан некорректно - ' + str(type(alid)))
			return False		
		return True

	def get_all_albums_ids(self):
		rows = self.albums.rows
		if type(rows) == type({}):
			return list(rows.keys())
		return 0

	def get_all_albums_photos(self, alid):
		rows = self.albums.rows
		if type(rows) == type({}) and int(alid) in rows.keys():
			return [key for key in rows[int(alid)].keys() if int(key) != -1]
		return 0

	def get_album_photo_path(self, alid, imid):	
		rows = self.albums.rows
		objects = self.albums
		if type(rows) == type({}) and int(alid) in rows.keys() and int(imid) in rows[int(alid)].keys() and 'filename' in rows[int(alid)][int(imid)].keys():
			return objects.files_manager.get_path_to_file(alid, rows[int(alid)][int(imid)]['filename'])
		return 0

	def get_album_data(self, alid, phid=-1):	
		rows = self.albums.rows
		if type(rows) == type({}) and int(alid) in rows.keys() and int(phid) in rows[int(alid)].keys():
			return rows[int(alid)][int(phid)]
		return 0

	#### EVENTS ######
	def add_event(self, event_data):
		res = []
		data = event_data
		objects = self.events
		if type(data) == type({}):
			res.append( objects.add_object(data) )
		elif type(data) == type([]):
			for p in data:
				res.append( objects.add_object(p) )
		else:
			print('тип event_data при добавлении задан некорректно - ' + str(type(relation_data)) )
		#objects.save()
		return res

	def edit_event(self, event_data):
		data = event_data
		objects = self.events
		if type(data) == type({}) and objects.pkey in data.keys() and objects.lkey in data.keys():			
			return objects.edit_object(data)
			#objects.save()
			#return True
		return False

	def del_event(self, event_data):
		data = event_data
		objects = self.events
		if type(data) == type({}) and objects.pkey in data.keys() and objects.lkey in data.keys():
			pid = int(data[objects.pkey])	
			lid = int(data[objects.lkey])		
			if objects.del_list_record(pid, lid):
				print('Запись успешно удалена - ' + str(pid))
				#self.photos.save()
				return True
			else:
				print('Запись не удалена - ' + str(pid))
		return False

	def del_all_events(self, pid):		
		if type(pid) == type(1):
			self.events.del_object(int(pid))
		elif type(pid) == type([]):
			for p in pid:
				self.del_all_events(int(p))
		else:
			print('тип pid при удалении задан некорректно - ' + type(pid))
			return False
		#self.photos.save()
		return True

	def get_event_data(self, pid, phid):	
		rows = self.events.rows
		if type(rows) == type({}) and int(pid) in rows.keys() and int(phid) in rows[int(pid)].keys():
			return rows[int(pid)][int(phid)]
		return 0

	def get_all_event_ids(self, pid):
		rows = self.events.rows
		if type(rows) == type({}) and int(pid) in rows.keys():
			return list(rows[int(pid)].keys())
		return 0


def read_json(filename):
	with open(filename, 'r') as f:
		# Reading from json file 
		d = json.load(f)
		return d
	return 0	

def fill_table_and_save(filename, table):
	data = read_json(filename)
	for e in data:
		table.add_object(e)
		print(e)
	table.save()

def clear_table(pkey, table):
	del_ids = [e for e in table.rows.keys()]
	for pid in del_ids:
		table.del_object(pid)
	table.save()
	#print(del_ids)

def find_event_by_date(db, alid, date):
	if type(db.events.rows) == type({}) and alid in db.events.rows.keys():
		events = db.events.rows[alid]
		if type(events) == type({}):
			for key in events.keys():
				if events[key]['event_head'] == date:
					return events[key]
	return 0



if __name__ == '__main__':
	pass
	db = AllTables('database/objects')

	# Как перенести альбом из моего телефона
	url = r'C:\Users\Zver\treefamily\Camera'
	files = os.listdir(url)
	img_count = 0
	vid_count = 0
	oth_count = 0
	err_count = 0
	res = []
	#res = db.add_album({'imid': -1, 'title': 'Телефон Вани'})
	if len(res) == 1:
		album = res[0]
		print(album)
		for f in files:
			print(f)
			parse_lst = f.split('_')
			if len(parse_lst) == 3:
				if parse_lst[0] == 'IMG':
					year, month, day = parse_lst[1][0:4], parse_lst[1][4:6], parse_lst[1][6:]
					res_data = db.add_album({'alid': album['alid'],  'oldpath': os.path.join(url, f)})
					if len(res_data) == 1:
						imid = res_data[0]['imid']
						event_head = day + '.' + month + '.' + year
						event = find_event_by_date(db, album['alid'], event_head)
						#print(event)
						#input()
						if event:
							event['photo_ids'] = event['photo_ids'] + [imid]
							db.edit_event(event)								
						else:
							db.add_event({'alid': album['alid'], 'event_head': event_head, 'event_desc': '', 'photo_ids' : [imid]})
						db.events.save()
					else:
						err_count = err_count + 1
					
					img_count = img_count + 1
				
				if parse_lst[0] == 'VID':
					year, month, day = parse_lst[1][0:4], parse_lst[1][4:6], parse_lst[1][6:]
					res_data = db.add_album({'alid': album['alid'],  'oldpath': os.path.join(url, f), 'video': True})
					if len(res_data) == 1:
						imid = res_data[0]['imid']
						event_head = day + '.' + month + '.' + year
						event = find_event_by_date(db, album['alid'], event_head)
						#print(event)
						#input()
						if event:
							event['photo_ids'] = event['photo_ids'] + [imid]
							db.edit_event(event)								
						else:
							db.add_event({'alid': album['alid'], 'event_head': event_head, 'event_desc': '', 'photo_ids' : [imid]})
						db.events.save()
					else:
						err_count = err_count + 1
					vid_count = vid_count + 1

			if len(parse_lst) > 3:
				for i, e in enumerate(parse_lst):
					if e == 'IMG':
						img_count = img_count + 1
					if e == 'VID':
						year, month, day = parse_lst[i+1][0:4], parse_lst[i+1][4:6], parse_lst[i+1][6:]
						print((year, month, day))

						res_data = db.add_album({'alid': album['alid'],  'oldpath': os.path.join(url, f), 'video': True})
						if len(res_data) == 1:
							imid = res_data[0]['imid']
							event_head = day + '.' + month + '.' + year
							event = find_event_by_date(db, album['alid'], event_head)
							#print(event)
							#input()
							if event:
								event['photo_ids'] = event['photo_ids'] + [imid]
								db.edit_event(event)								
							else:
								db.add_event({'alid': album['alid'], 'event_head': event_head, 'event_desc': '', 'photo_ids' : [imid]})
							db.events.save()
						else:
							err_count = err_count + 1
						vid_count = vid_count + 1

		print('ERRORS = ' + str(err_count))
		print('IMAGES = ' + str(img_count))
		print('VIDEOS = ' + str(vid_count))
		print('ALL = ' + str(vid_count + img_count))
		print(len(files))
	print(db.events)
	#db.del_all_events(1)
	#db.events.save()
	#db.del_album(1)
	print(db.albums)

	#################
	### ALBUMS  #####
	#################
	# Добавить новый альбом
	#db.add_album({'imid': -1, 'name': 'Альбом'})
	# Добавить новую фотографию в альбом
	#db.add_album({'alid': 3,  'oldpath': r'C:\1\1.jpg'})
	
	# Переименовтаь альбом
	#db.edit_album({'alid': 3, 'imid': -1, 'name': 'Альбом3'})

	# Удалить альбом
	#db.del_album(1)
	# Удалить фото из альбома
	#db.del_photo_from_album({'alid': 1, 'imid': 1})

	#print(db.events)
	#################
	### EVENTS  #####
	#################	
	
	#{'alid': 0, 'eid': 0, 'event_head': '', 'event_desc': '', 'event_date': '',
	#					'place': '', 'person_years': '', 'photo_id': ''}
	# Добавить событие
	#db.add_event({'alid': 1, 'event_head': 'Свадьба', 'event_desc': '<hfrcsfsdsdfs'})
	
	# Редактировать событие 
	#db.edit_event({'alid': 1, 'eid': 1, 'event_head': '-Свадьба-'})
	
	# Удалить конкретное событие для alid
	#db.del_event({'alid': 1, 'eid': 2})
	
	# Удалить все события для данного alid
	#db.del_all_events(1)
			
	#print(db.events.rows)
	#db.events.save()
	#print(db.events)
	
	#################
	### DOCS    #####
	#################
	
	# !!! Любое изменение сразу сохраняется в базе данных

	# Добавить документ
	#db.add_doc({'pid': 1, 'oldpath': r'C:\1\log_descriptions.txt'})
	
	# Редактировать документ (возможно без указания oldpath если документ не заменяется)
	#db.edit_doc({'pid': 1, 'did': 1, 'oldpath': r'C:\1\common.pdf'})
	
	# Удалить конкретный документ для pid
	#db.del_doc({'pid': 1, 'did': 2})
	
	# Удалить все документы для данного pid
	#db.del_all_docs(1)
			
	#print(db.photos.rows)
	#print(db.docs)
	#print(db.get_photo_path(1, 1))



	#################
	### PHOTOS  #####
	#################
	
	# !!! Любое изменение сразу сохраняется в базе данных

	# Добавить фото
	#db.add_photo({'pid': 1, 'oldpath': r'C:\1\1.jpg'})
	
	# Редактировать фото (возможно без указания oldpath если фото не заменяется)
	#db.edit_photo({'pid': 1, 'phid': 1, 'oldpath': r'C:\1\1.jpg'})
	
	# Удалить конкретное фото для pid
	#db.del_photo({'pid': 1, 'phid': 6})
	
	# Удалить все фото для данного pid
 	#db.del_all_photo(1)
			
	#print(db.photos.rows)
	#print(db.photos)
	#print(db.get_photo_path(1, 1))

	#################
	### FILES   #####
	#################

	#f = Files('database/objects')
	
	# How to import photos
	#data = read_json('photos_export.json')
	#for e in data:
	#	print(e)
	#	print(db.add_photo(e))

	# How to import peoples
	# Clear all records if needed
	#clear_table('pid', db.peoples)
	#fill_table_and_save('peoples_export.json', db.peoples)
	#print(db.peoples.rows)
	

	# How to import relations
	# Clear all records if needed
	#clear_table('pid', db.relations)
	#fill_table_and_save('relations_export.json', db.relations)
	#print(db.relations.rows)


	# How to work with database
	#print(db.peoples.rows()) 
	
	#################
	### PEOPLES #####
	#################

	# How to read peoples dict
	#peoples = Peoples('database/objects', 'peoples')
	
	# How to add people (need save)
	#peoples.add_object({'pid':'1', 'rid': '2', 'name': 'Petr'})

	# How to edit people (pid, data)    (need save)
	#peoples.edit_object(1, {'rid': '2', 'name': 'John'})

	# How to del people  (need save)
	#peoples.del_object(15)
	
	# How to commit changes
	#peoples.save()

	# How to show peoples
	#print(peoples.rows)

	#################
	### EVENTS ######
	#################

	#events = Events('database/objects', 'events')
	#print(events.add_object({'pid': 70, 'event_head': 'Со', 'event_desc': ''}))
	#print(events.del_object(70)) # +
	#print(events.edit_object({'pid': 70, 'eid': 2, 'event_head': 'Сообщество', 'event_desc': '123'}))
	
	#################
	### RELATIONS ###
	#################

	# How to read relations dict
	#relations = Relations('database/objects', 'relations')
	
	# How to add relation (need save) 1 - 4 relatives 	
	#relations.add_object({'pid': 11, 'typeid': MOTHER, 'ppid': 3})
	# 5 - N partners
	#relations.add_object({'pid': 11, 'typeid': 3, 'ppid': 45})
	
	# How to edit relation (need save)
	#relations.edit_object({'pid': 11, 'typeid': 6, 'ppid': 12})

	# How to del relation (need save) all list records	
	#print(relations.del_object(12))
	# Only one record
	#relations.del_list_record(11,5)
	
	# How to commit changes
	#relations.save()
	
	# How to show relations
	#print(relations.rows)
	
