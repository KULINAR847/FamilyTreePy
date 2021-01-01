from graphviz import Digraph, Graph
from driver import AllTables
import os
#import pandas as pd
import json
from gallery_miniature import GalleryMiniature

class GraphDrawer:
    def __init__(self, db=0, rengine='dot'):
        self.db = db
        self.dot = Digraph(comment='The Round Table', node_attr={'color': 'lightblue2', 'style': 'filled'}, engine=rengine) #node_attr={'color': 'lightblue2', 'style': 'filled'},
        self.dot.attr(newrank='true')
        #self.dot.attr(rankdir='TB')  
        self.dot.attr(pad="0.5")  
        self.dot.attr(ranksep="1")
        #self.dot.attr(nodesep="2.0")
        
        self.dot.attr(ratio = "auto")
        self.dot.attr(remincross = "false")
        self.dot.attr(label = "FAMILY TREE")

        self.fill_nodes()
        self.set_ranks()
        self.fill_relations()
        #self.set_rel_ranks()
        self.dot.format = 'svg'
        self.dot.render(view=True)#('round-table.gv', view=True)  


    def set_ranks(self):
        pids = sorted(list(self.db.peoples.rows.keys()), reverse=False)
        p0000 = Digraph(name='0000-')
        p0000.attr(rank='same')          
        #p0000.body.append("rankdir=LR")
        #p0000.attr(rankdir='LR')
        p1000 = Digraph(name='1000-') 
        p1000.attr(rank='same')
        #p1000.attr(sortv="1")   
        #p1000.body.append("rankdir=LR")
        #p1000.attr(rankdir='LR')
        p2000 = Digraph(name='2000-')
        p2000.attr(rank='same') 
        #p2000.attr(sortv="2")   
        #p2000.body.append("rankdir=LR")
        #p2000.attr(rankdir='LR') 
        p3000 = Digraph(name='3000-')
        p3000.attr(rank='same') 
        #p3000.attr(sortv="3")   
        #p3000.body.append("rankdir=LR")
        #p3000.attr(rankdir='LR') 
        p4000 = Digraph(name='4000-') 
        p4000.attr(rank='same')
        #p4000.attr(sortv="1")   
        #p4000.body.append("rankdir=LR")
        #p4000.attr(rankdir='LR')
        p5000 = Digraph(name='5000-') 
        p5000.attr(rank='same')  
        #p5000.body.append("rankdir=LR") 
        #p5000.attr(sortv="1")        
        for pid in pids:
            if pid > 0 and pid < 1000:
                p0000.node(str(pid))
            if pid >= 1000 and pid < 2000:
                p1000.node(str(pid))
            if pid >= 2000 and pid < 3000:
                p2000.node(str(pid))
            if pid >= 3000 and pid < 4000:
                p3000.node(str(pid))
            if pid >= 4000 and pid < 5000:
                p4000.node(str(pid))
            if pid >= 5000 and pid < 6000:
                p5000.node(str(pid))

        self.dot.subgraph(p0000)
        self.dot.subgraph(p1000)
        self.dot.subgraph(p2000)
        self.dot.subgraph(p3000)
        self.dot.subgraph(p4000)
        self.dot.subgraph(p5000)

    def set_rel_ranks(self, rels):
        pids = sorted([int(key) for key in rels.keys() if '_im' not in key], reverse=False)
        print(pids)
        p0000 = Digraph(name='0000-')
        p0000.attr(rank='same')          
        #p0000.body.append("rankdir=LR")
        #p0000.attr(rankdir='LR')
        p1000 = Digraph(name='1000-') 
        p1000.attr(rank='same')
        #p1000.attr(sortv="1")   
        #p1000.body.append("rankdir=LR")
        #p1000.attr(rankdir='LR')
        p2000 = Digraph(name='2000-')
        p2000.attr(rank='same') 
        #p2000.attr(sortv="2")   
        #p2000.body.append("rankdir=LR")
        #p2000.attr(rankdir='LR') 
        p3000 = Digraph(name='3000-')
        p3000.attr(rank='same') 
        #p3000.attr(sortv="3")   
        #p3000.body.append("rankdir=LR")
        #p3000.attr(rankdir='LR') 
        p4000 = Digraph(name='4000-') 
        p4000.attr(rank='same')
        #p4000.attr(sortv="1")   
        #p4000.body.append("rankdir=LR")
        #p4000.attr(rankdir='LR')
        p5000 = Digraph(name='5000-') 
        p5000.attr(rank='same')  
        #p5000.body.append("rankdir=LR") 
        #p5000.attr(sortv="1")        
        for pid in pids:
            if pid > 0 and pid < 1000:
                p0000.node(rels[str(pid)])
            if pid >= 1000 and pid < 2000:
                p1000.node(rels[str(pid)])
            if pid >= 2000 and pid < 3000:
                p2000.node(rels[str(pid)])
            if pid >= 3000 and pid < 4000:
                p3000.node(rels[str(pid)])
            if pid >= 4000 and pid < 5000:
                p4000.node(rels[str(pid)])
            if pid >= 5000 and pid < 6000:
                p5000.node(rels[str(pid)])

        self.dot.subgraph(p0000)
        self.dot.subgraph(p1000)
        self.dot.subgraph(p2000)
        self.dot.subgraph(p3000)
        self.dot.subgraph(p4000)
        self.dot.subgraph(p5000)
    
    def fill_nodes(self):
        pids = sorted(list(self.db.peoples.rows.keys()), reverse=False)
        for pid in pids:
            people = self.db.get_people(pid)        
            text , color_rel = self.get_people_info(pid) 

            photo_ids = self.db.get_all_photo_ids(pid)
            image_path = self.db.get_photo_path(pid, photo_ids[0]) if photo_ids and type(photo_ids) == type([]) and len(photo_ids) > 0 else ''
            image_mini_path = os.path.join( os.path.join('photos', 'miniatures'), str(pid) + '_001.png')
            if image_path != '' and os.path.exists(image_path) and not os.path.exists(image_mini_path):
                print(pid)
                gm = GalleryMiniature(pid, image_path)
                gm.exec()  

            shape = 'doublecircle'
            #else:
            #    shape = 'doubleoctagon'
            node_text = str(people['pid'])
            node_image = str(people['pid']) + '_im'
            node_tooltip = str( 'День рождения: ' + str(people['birthday']) + '' if 'birthday' in people.keys() and str(people['birthday']) != '' else '' )
            node_image_tooltip = r'<img src="photos/miniatures/4009_001.png" width="189" height="255">'
            #node_tooltip = node_tooltip + node_tooltip
            self.dot.node(node_text, text, shape='box', color=color_rel, fontcolor='white', width="3", height="2", fixedsize="true", fontsize="36", tooltip=node_tooltip ) #image="f.png",'''
            if os.path.exists(image_mini_path):
                self.dot.node(node_image, '', shape=shape, color=color_rel, fontcolor='white', tooltip=node_image_tooltip, image=image_mini_path, imagescale="true", width="3", height="3", fixedsize="true", fontsize="36") #image="f.png",'''
            else:
                self.dot.node(node_image, '', shape=shape, color=color_rel, fontcolor='white', width="3", height="3", fixedsize="true", fontsize="36") #image="f.png",'''

            self.dot.edge(node_image, node_text, weigth="1400")
            
    def get_people_info(self, pid):
        people = self.db.get_people(int(pid))
        text_formatter = lambda x: x if x == '' else '\n'.join(str(x).split(' ')) + '\n'
        text = text_formatter(people['surname']) + str('' if people['maiden'] == '' else '(' + people['maiden'] + ')\n') +  text_formatter(people['name']) + text_formatter(people['midname'])
        pol = people['pol'] if 'pol' in people.keys() else ''
        if pol == '':
            color_rel = "/dark28/"+str(2)					
        if len(pol) > 0 and pol[0].lower() == 'м':
            #text = text_formatter(self.mans_surnames[random.randint(0, len(self.mans_surnames)-1)]) +  text_formatter(self.mans_names[random.randint(0, len(self.mans_names)-1)])
            color_rel = "#ad66d5"#"/dark28/"+str(3)
        if len(pol) > 0 and pol[0].lower() == 'ж':
            #text = text_formatter(self.womans_surnames[random.randint(0, len(self.womans_surnames)-1)]) +  text_formatter(self.womans_names[random.randint(0, len(self.womans_names)-1)])
            color_rel = "#e667af"#"/dark28/"+str(8)
        #is_alive = people['deathday'] if 'deathday' in people.keys() else ''

        return (text, color_rel)

    def have_parents(self, pid):
        relations = self.db.get_relations(int(pid))
        rel_keys = sorted([typeid for typeid in relations]) if relations else []
        if 1 in rel_keys or 2 in rel_keys:
            return True
        return False

    def fill_relations(self):
        pids = sorted(list(self.db.peoples.rows.keys()), reverse=True)
        #print(pids)
        rel_nodes = {}
        pids_added = []
        for pid in pids:            
            relations = self.db.get_relations(pid)
            rel_keys = sorted([typeid for typeid in relations]) if relations else []
            #print(relations)
            for key in rel_keys:
                if key > 2:
                    #print(relations[key])
                    people_pid1 = str(relations[key]['ppid'])
                    people_pid2 = str(relations[key]['pid'])   
                    people_pid_im1 = str(relations[key]['ppid']) + '_im'
                    people_pid_im2 = str(relations[key]['pid']) + '_im' 
                    #print((people_pid1,people_pid2))                 
                    if people_pid2 in rel_nodes.keys():
                        node_need_add = False
                    else:
                        node_need_add = True
                        rel_nodes[people_pid1] = people_pid1 + '_' + people_pid2
                        rel_nodes[people_pid2] = people_pid1 + '_' + people_pid2
                        rel_nodes[people_pid_im1] = people_pid1 + '_' + people_pid2
                        rel_nodes[people_pid_im2] = people_pid1 + '_' + people_pid2


                    #rel_nodes[people_pid_im1] = people_pid_im1 + people_pid_im2
                    #rel_nodes[people_pid_im2] = people_pid_im1 + people_pid_im2
                    #print(rel_nodes)
                    if node_need_add:
                        self.dot.node(rel_nodes[people_pid2], '', shape='invtriangle', color=str("/dark28/"+str(2)), width="0.7", height="0.7", fixedsize="true")
                        #self.dot.node(rel_nodes[people_pid_im2], '', shape='invtriangle', color=str("/dark28/"+str(2)), width="1.5", height="1.5", fixedsize="true")
                        #self.dot.edge(people_pid2, people_pid1, color="#e1004c")
                    self.dot.edge(people_pid2, rel_nodes[people_pid2], color="#e1004c", weigth="5000")
                    self.dot.edge(people_pid_im2, rel_nodes[people_pid_im2], style="invis", constraint="false", weigth="5000") #style="invis"
                    self.dot.edge(people_pid2, rel_nodes[people_pid2], style="invis", weigth="5000")
        
        #print(rel_nodes)
            #print(rel_keys) 
        
        print(rel_nodes)
        for pid in pids:
            relations = self.db.get_relations(pid)
            #print(relations)
            rel_keys = sorted([typeid for typeid in relations]) if relations else []
            for key in rel_keys:
                if key == 1 or key == 2:
                    if str(relations[key]['ppid']) in rel_nodes.keys():
                        self.dot.edge(rel_nodes[str(relations[key]['ppid'])], str(relations[key]['pid']), color="#3714b0", weigth="10000")#color="#7908aa")
                        #self.dot.edge(rel_nodes[str(relations[key]['ppid'])], str(relations[key]['ppid']), color="#3714b0", weigth="10000")
                        #self.dot.edge(rel_nodes[str(relations[key]['ppid'])], str(relations[key]['pid']), style="invis", weigth="10000")
                        break
                    self.dot.edge(str(relations[key]['ppid']), str(relations[key]['pid']), color="#3714b0", weigth="1000")
                    #self.dot.edge(str(relations[key]['ppid']) + '_im', str(relations[key]['pid']) + '_im', style="invis", constraint="false", weigth="100000")
                    #self.dot.edge(str(relations[key]['ppid']), str(relations[key]['pid']), style="invis", weigth="10000")


if __name__ == '__main__':
    db = AllTables('database/objects')
    graph = GraphDrawer(db)