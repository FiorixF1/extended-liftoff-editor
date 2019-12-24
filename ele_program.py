import os
import xml.etree.ElementTree as ET
from PIL import Image

import ele_utils

class Program:
    def __init__(self):
        self.blueprints = dict()
        self.previews = dict()
        self.instances = list()
        self.instance_id_counter = 0

    def init(self):
        for xml_file in os.listdir("./blueprints"):
            if xml_file.endswith(".xml"):
                name = xml_file[:-4]
                blueprint = ele_utils.Blueprint(name)
                self.blueprints[name] = blueprint
                
                '''
                Structure of the XML model (note the XSD declaration in the root tag, not present in Liftoff files but required here for parsing)
                
                <blueprints xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
                  <TrackBlueprint xsi:type="TrackBlueprintFlag">
                    <itemID>...</itemID>
                    <instanceID>...</instanceID>
                    <position>
                      <x>...</x>
                      <y>...</y>
                      <z>...</z>
                    </position>
                    <rotation>
                      <x>...</x>
                      <y>...</y>
                      <z>...</z>
                    </rotation>
                    <purpose>Functional</purpose>
                  </TrackBlueprint>
                </blueprints>
                '''
                
                root = ET.parse("./blueprints/{}".format(xml_file)).getroot()
                for TrackBlueprint in root:
                    itemID = TrackBlueprint[0].text
                    instanceID = TrackBlueprint[1].text

                    pos_x = float(TrackBlueprint[2][0].text)
                    pos_y = float(TrackBlueprint[2][1].text)
                    pos_z = float(TrackBlueprint[2][2].text)

                    rot_x = float(TrackBlueprint[3][0].text)
                    rot_y = float(TrackBlueprint[3][1].text)
                    rot_z = float(TrackBlueprint[3][2].text)
                    
                    this_item = ele_utils.Item(itemID, instanceID, pos_x, pos_y, pos_z, rot_x, rot_y, rot_z)
                    blueprint.add(this_item)
                
                # load blueprint preview if existing
                try:
                    image = Image.open("./blueprints/{}.png".format(name))
                    self.previews[name] = image
                except:
                    pass
        return tuple(self.blueprints.keys())

    def add_instance(self, name, x, y, z, pitch, yaw, roll):
        new_instance = self.blueprints[name].copy()
        self.instance_id_counter = new_instance.sync_instance_id(self.instance_id_counter)
        
        new_instance.translate(x, y, z)
        new_instance.rotate(pitch, yaw, roll)
        
        self.instances.append(new_instance)
        
        return new_instance.pretty_print()

    def remove_instance(self, index):
        del self.instances[index]

    def load_project(self, file):
        with open(file, "r") as file:
            data = file.read().split('\n')
                
        self.instances = list()
        for instance in data:
            values = instance.split(':')
            name = values[0]
            x, y, z, pitch, yaw, roll = map(lambda x: float(x), values[1:])
                    
            new_instance = self.blueprints[name].copy()
            self.instance_id_counter = new_instance.sync_instance_id(self.instance_id_counter)
                
            new_instance.translate(x, y, z)
            new_instance.rotate(pitch, yaw, roll)
            
            self.instances.append(new_instance)
            
        return map(lambda x: x.pretty_print(), self.instances)
        
    def save_project(self, file):
        output = '\n'.join(map(lambda instance: instance.serialize(), self.instances))
        file.write(output)

    def generate_xml(self, file):
        xml_output = '  <blueprints>'
        for instance in self.instances:
            xml_output += str(instance)
        xml_output += '\n  </blueprints>'
        xml_output += '\n  <lastTrackItemID>{}</lastTrackItemID>'.format(self.instance_id_counter)
        file.write(xml_output)
