#!/usr/bin/env python3

import sys
import os
import re
import importlib
from pxr import Usd
from owlready2 import onto_path, get_ontology

class_set = set()
prim_classes = dict()


def usd_to_owl(file_path: str) -> None:
    stage = Usd.Stage.Open(file_path)
    for prim in stage.Traverse():
        for prop in prim.GetPropertyNames():
            if 'semanticType' in prop and prim.GetAttribute(prop).Get() == 'class':
                prop = prop.replace('Type', 'Data')
                prim_class = prim.GetAttribute(prop).Get()
                class_set.add(prim_class)
                prim_classes[prim.GetName()] = prim_class
                break

    onto_path.append('examples/OWL')
    
    # Create the folder if it doesn't exist
    if not os.path.exists(onto_path[0]):
        os.makedirs(onto_path[0])

    TBox_onto = get_ontology('http://iai_apartment/TBox.owl')
    ABox_onto = get_ontology('http://iai_apartment/ABox.owl')

    soma_onto = get_ontology(
        'http://www.ease-crc.org/ont/SOMA.owl')
    soma_onto.load()
    soma_home_onto = get_ontology(
        'http://www.ease-crc.org/ont/SOMA-HOME.owl')
    soma_home_onto.load()

    TBox_onto.imported_ontologies.append(soma_onto)
    TBox_onto.imported_ontologies.append(soma_home_onto)

    ABox_onto.imported_ontologies.append(TBox_onto)

    with TBox_onto:
        class IslandCover(soma_onto.DesignedComponent):
            pass

        class WindowFrame(soma_onto.Rack):
            pass
    
    with ABox_onto:
        for prim_name, prim_class in prim_classes.items():
            if (onto:=eval('TBox_onto.' + prim_class)) != None or (onto:=eval('soma_onto.' + prim_class)) != None or (onto:=eval('soma_home_onto.' + prim_class)):
                onto(prim_name)
            else:
                prim_class_list = re.findall('[A-Z][^A-Z]*', prim_class)
                prim_class_list.reverse()

                prim_class_to_search = ''
                for prim_class_element in prim_class_list:
                    prim_class_to_search = prim_class_to_search + prim_class_element
                    if (onto:=eval('TBox_onto.' + prim_class_to_search)) != None or (onto:=eval('soma_onto.' + prim_class_to_search)) != None or (onto:=eval('soma_home_onto.' + prim_class_to_search)):
                        break
                if onto == None:
                    onto = TBox_onto.search_one(iri='*DesignedComponent')
                with TBox_onto:
                    exec('class %s(%s):\n\tpass' %(prim_class, 'onto'))
                eval('%s("%s")' %(prim_class, prim_name))
                print('Create new class\t%s <-- %s' %(TBox_onto.search_one(iri='*'+prim_class), str(onto)))

    TBox_onto.save(file=onto_path[0] + '/TBox.owl')
    ABox_onto.save(file=onto_path[0] + '/ABox.owl')
    return None
