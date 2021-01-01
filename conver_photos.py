import os
import json

def write_json(filename, d = 0):
    with open(filename, 'w') as f: 
        f.write(json.dumps(d)) 

files = os.listdir('photos')
#print(files)
new_data = []
root = os.path.join( os.getcwd(), 'photos' )

for f in files:
    if len(f.split('_')) == 2 and '001' in f:
        print(f) 
        d = {}
        d['pid'] = int(f.split('_')[0])
        d['oldpath'] = os.path.join( root, f )
        new_data.append(d)
print(new_data)
# new_data_rids = []
# new_data_peoples = []
# data = self.peoples.data
# for e in data:
#     new_data_rids.append([e[self.peoples.columns.index('id')], e[self.peoples.columns.index('rid')]])
#     d = {}
#     d['pid'] = e[self.peoples.columns.index('id')]
#     d['surname'] = e[self.peoples.columns.index('surname')]
#     d['maiden'] = e[self.peoples.columns.index('maiden')]
#     d['name'] = e[self.peoples.columns.index('name')]
#     d['midname'] = e[self.peoples.columns.index('midname')]
#     d['birthday'] = e[self.peoples.columns.index('date_begin')]
#     d['deathday'] = e[self.peoples.columns.index('date_end')]
#     d['pol'] = e[self.peoples.columns.index('pol')]
#     new_data_peoples.append(d)

#print(new_data_rids)
#rids_parents = [int(e[1]) for e in new_data_rids if str(e[1]) != '']
write_json('photos_export.json', new_data)