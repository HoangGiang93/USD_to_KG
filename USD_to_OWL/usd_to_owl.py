#!/usr/bin/env python3

import sys
import os
from pxr import Usd
from owlready2 import onto_path, get_ontology

type_set = set()
prim_types = dict()


def usd_to_owl(file_path: str) -> None:
    stage = Usd.Stage.Open(file_path)
    for prim in stage.Traverse():
        for prop in prim.GetPropertyNames():
            if 'semanticType' in prop and prim.GetAttribute(prop).Get() == 'class':
                prop = prop.replace('Type', 'Data')
                prim_type = prim.GetAttribute(prop).Get()
                type_set.add(prim_type)
                prim_types[prim.GetName()] = prim_type
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
        class CabinetDrawer(soma_onto.Drawer):
            pass

        class FridgeDrawer(soma_onto.Drawer):
            pass

        class CoffeeTableDrawer(soma_onto.Drawer):
            pass

        class SinkDrawer(soma_onto.Drawer):
            pass

        class CabinetDoor(soma_onto.Door):
            pass

        class WardrobeDoor(soma_onto.Door):
            pass

        class OvenDoor(soma_onto.Door):
            pass

        class FridgeDoor(soma_onto.Door):
            pass

        class IslandCover(soma_onto.DesignedComponent):
            pass

        class Window(soma_onto.DesignedComponent):
            pass

        class WindowFrame(soma_onto.Rack):
            pass

    with ABox_onto:
        for prim_name, prim_type in prim_types.items():
            if len(onto:=TBox_onto.search(iri='*'+prim_type)) == 1:
                onto[0](prim_name)
            else:
                print(prim_type, 'not found', file=sys.stderr)

    TBox_onto.save(file=onto_path[0] + '/TBox.owl')
    ABox_onto.save(file=onto_path[0] + '/ABox.owl')
    return None
