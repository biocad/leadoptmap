import mcs
import os
import struc
import sys
from kbase import KBASE
import hashlib

#calculate similarity scores of molecule pair based on giving rule. Give back the score matrix correspoding to the molecule title and id. 
def matrix ( mols, mcs_ids, rule ):
    import numpy
    id_list = []
    id_vs_simi = {}
    id_vs_title = {}
    title_vs_simi = {}
    title_list = []
    filename_vs_title = {}
    for mol in mols:
        #generate dictionary of id vs title of giving mols
        title = mol.title()
        id = mol.id()
        file_path = KBASE.ask (id, "filename")
        filename = os.path.basename(file_path)
        if id not in id_list:
            id_list.append(id)
        if title not in title_list:
            title_list.append(title)
        id_vs_title [id] = title
        filename_vs_title [filename] = title
    for id in mcs_ids:
        #generate dictionary of pair's title vs similarity score
        id0, id1 = mcs.get_parent_ids(id)
        simi       = rule.similarity( id0, id1, mcs_id = id )        
        title0 = id_vs_title[id0]
        title1 = id_vs_title[id1]
        title_vs_simi [(title0,title1)] = simi
    #generate the score matrix 
    size          = len( title_list )
    scores = numpy.zeros( (size, size,) )
    for i in range( size ) :
            scores[i, i] = 1.0
            for j in range( i + 1, size ) :
                title_i = title_list[i]
                title_j = title_list[j]
                if title_vs_simi.has_key((title_i,title_j)):
                    simi = title_vs_simi[(title_i,title_j)]
                    scores[i, j] = simi                
                    scores[j, i] = simi

    return (title_list, id_list,filename_vs_title, scores)                
# add mcs id to each edge of giving graph for the later layout. 
def add_mcs_id( mcs_id_list, graph ):
    for edge in graph.edges(data = True):
        mol0_id = edge[0]
        mol1_id = edge[1]
        mol0 = KBASE.ask( mol0_id )
        mol1 = KBASE.ask( mol1_id )
        name0 = mol0.title()
        name1 = mol1.title()
        mcs_title = "mcs@%s..%s" % (name0, name1,)
        mcs_id = hashlib.sha1( mcs_title ).hexdigest()
        if mcs_id not in mcs_id_list:
            # the first mcs_id is not in id list need to generate reverse one 
            mcs_title = "mcs@%s..%s" % (name1, name0,)
            mcs_id = hashlib.sha1( mcs_title ).hexdigest() 
            if mcs_id not in mcs_id_list:
                sys.exit()   
        graph.add_edge(mol0_id, mol1_id, mcs_id = mcs_id)
        
