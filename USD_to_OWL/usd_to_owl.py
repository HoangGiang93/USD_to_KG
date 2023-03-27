#!/usr/bin/env python3

import os
import re
from pxr import Usd
from owlready2 import onto_path, get_ontology

prim_classes = dict()


def get_class_from_ontology(ontos: list, class_name: str):
    for onto in ontos:
        if (found_class := getattr(onto, class_name)) != None:
            return found_class
    return None


def import_ontologies(url_list: list):
    ontos = []
    for url in url_list:
        onto = get_ontology(url)
        onto.load()
        ontos.append(onto)
    return ontos


def usd_to_owl(file_path: str) -> None:
    # Collect prim_classes
    stage = Usd.Stage.Open(file_path)
    for prim in stage.Traverse():
        for prop in prim.GetPropertyNames():
            if 'semanticType' in prop and prim.GetAttribute(prop).Get() == 'class':
                prop = prop.replace('Type', 'Data')
                prim_class = prim.GetAttribute(prop).Get()
                prim_classes[prim.GetName()] = prim_class
                break

    # Initialize onto_path
    onto_path.append('examples/OWL')

    # Create the folder if it doesn't exist
    if not os.path.exists(onto_path[0]):
        os.makedirs(onto_path[0])

    # Import ontologies
    ontos = import_ontologies(['http://www.ease-crc.org/ont/SOMA.owl',
                               'http://www.ease-crc.org/ont/SOMA-HOME.owl'])

    # Initialize TBox and ABox
    TBox_onto = get_ontology('http://iai_apartment/TBox.owl')
    ABox_onto = get_ontology('http://iai_apartment/ABox.owl')
    for onto in ontos:
        TBox_onto.imported_ontologies.append(onto)

    [soma_onto, _] = ontos
    with TBox_onto:
        class IslandCover(soma_onto.DesignedComponent):
            pass

        class WindowFrame(soma_onto.Rack):
            pass

    # Write ABox
    ontos.append(TBox_onto)
    ABox_onto.imported_ontologies.append(TBox_onto)
    with ABox_onto:
        for prim_name, prim_class in prim_classes.items():
            if (onto := get_class_from_ontology(ontos, prim_class)) != None:
                onto(prim_name)
            else:
                prim_class_list = re.findall('[A-Z][^A-Z]*', prim_class)
                prim_class_list.reverse()

                prim_class_to_search = ''
                for prim_class_element in prim_class_list:
                    prim_class_to_search = prim_class_to_search + prim_class_element
                    if (onto := get_class_from_ontology(ontos, prim_class_to_search)) != None:
                        break
                if onto == None:
                    onto = TBox_onto.search_one(iri='*DesignedComponent')
                with TBox_onto:
                    exec('class %s(%s):\n\tpass' % (prim_class, 'onto'))
                exec('%s("%s")' % (prim_class, prim_name))
                print('Create new class\t%s <-- %s' %
                      (TBox_onto.search_one(iri='*'+prim_class), str(onto)))

    # Save TBox and ABox
    TBox_onto.save(file=onto_path[0] + '/TBox.owl')
    ABox_onto.save(file=onto_path[0] + '/ABox.owl')
    return None
