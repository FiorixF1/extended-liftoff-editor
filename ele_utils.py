import numpy as np
from math import cos, sin, pi



def get_translation_matrix(x, y, z):
    translation_matrix = np.zeros((4, 4))
    for i in range(4):
        translation_matrix[i, i] = 1
    translation_matrix[0, 3] = x
    translation_matrix[1, 3] = y
    translation_matrix[2, 3] = z
    
    return translation_matrix

def get_x_rotation_matrix(angle):
    radians = angle*pi/180

    rotation_matrix = np.zeros((4, 4))
    rotation_matrix[0, 0] = 1
    rotation_matrix[1, 1] = cos(radians)
    rotation_matrix[1, 2] = -sin(radians)
    rotation_matrix[2, 1] = sin(radians)
    rotation_matrix[2, 2] = cos(radians)
    rotation_matrix[3, 3] = 1

    return rotation_matrix

def get_y_rotation_matrix(angle):
    radians = angle*pi/180

    rotation_matrix = np.zeros((4, 4))
    rotation_matrix[0, 0] = cos(radians)
    rotation_matrix[0, 2] = sin(radians)
    rotation_matrix[1, 1] = 1
    rotation_matrix[2, 0] = -sin(radians)
    rotation_matrix[2, 2] = cos(radians)
    rotation_matrix[3, 3] = 1

    return rotation_matrix

def get_z_rotation_matrix(angle):
    radians = angle*pi/180

    rotation_matrix = np.zeros((4, 4))
    rotation_matrix[0, 0] = cos(radians)
    rotation_matrix[0, 1] = -sin(radians)
    rotation_matrix[1, 0] = sin(radians)
    rotation_matrix[1, 1] = cos(radians)
    rotation_matrix[2, 2] = 1
    rotation_matrix[3, 3] = 1

    return rotation_matrix



class Item:
    def __init__(self, item_id, instance_id, pos_x, pos_y, pos_z, rot_x, rot_y, rot_z):
        self.item_id = item_id
        self.instance_id = instance_id

        self.pos = np.zeros((4, 1))
        self.pos[0, 0] = pos_x
        self.pos[1, 0] = pos_y
        self.pos[2, 0] = pos_z
        self.pos[3, 0] = 1
        
        self.rot = np.zeros((3, 1))
        self.rot[0, 0] = rot_x
        self.rot[1, 0] = rot_y
        self.rot[2, 0] = rot_z

    def transform(self, transformation_matrix):
        self.pos = transformation_matrix @ self.pos

    def rotate_x(self, angle):
        new_angle = self.rot[0, 0] + angle
        while new_angle >= 360: new_angle -= 360
        while new_angle < 0:    new_angle += 360
        self.rot[0, 0] = new_angle

    def rotate_y(self, angle):
        new_angle = self.rot[1, 0] + angle
        while new_angle >= 360: new_angle -= 360
        while new_angle < 0:    new_angle += 360
        self.rot[1, 0] = new_angle

    def rotate_z(self, angle):
        new_angle = self.rot[2, 0] + angle
        while new_angle >= 360: new_angle -= 360
        while new_angle < 0:    new_angle += 360
        self.rot[2, 0] = new_angle

    def copy(self):
        return Item(self.item_id, self.instance_id, self.pos[0, 0], self.pos[1, 0], self.pos[2, 0], self.rot[0, 0], self.rot[1, 0], self.rot[2, 0])

    def __str__(self):
        return ('\n    <TrackBlueprint xsi:type="TrackBlueprintFlag">' + \
                '\n      <itemID>{}</itemID>' + \
                '\n      <instanceID>{}</instanceID>' + \
                '\n      <position>' + \
                '\n        <x>{}</x>' + \
                '\n        <y>{}</y>' + \
                '\n        <z>{}</z>' + \
                '\n      </position>' + \
                '\n      <rotation>' + \
                '\n        <x>{}</x>' + \
                '\n        <y>{}</y>' + \
                '\n        <z>{}</z>' + \
                '\n      </rotation>' + \
                '\n      <purpose>Functional</purpose>' + \
                '\n    </TrackBlueprint>').format(self.item_id,
                                                  self.instance_id,
                                                  round(self.pos[0, 0], 3),
                                                  round(self.pos[1, 0], 3),
                                                  round(self.pos[2, 0], 3),
                                                  round(self.rot[0, 0], 3),
                                                  round(self.rot[1, 0], 3),
                                                  round(self.rot[2, 0], 3))



class Blueprint:
    def __init__(self, name):
        self.name = name
        self.items = list()
        
        self.pos_x = 0
        self.pos_y = 0
        self.pos_z = 0
        
        self.rot_x = 0
        self.rot_y = 0
        self.rot_z = 0

    def translate(self, x, y, z):
        # translation of center
        self.pos_x += x
        self.pos_y += y
        self.pos_z += z
        
        # translation of items
        translation_matrix = get_translation_matrix(x, y, z)
        for item in self.items:
            item.transform(translation_matrix)

    # sequence for a generic rotation of a set of items:
    # - translate items in the origin
    # - rotate using transformation matrices
    # - translate back in the starting point
    # - rotate each single item modifying their attributes

    def rotate_x(self, angle):
        # rotation of center
        new_angle = self.rot_x + angle
        while new_angle >= 360: new_angle -= 360
        while new_angle < 0:    new_angle += 360
        self.rot_x = new_angle
        
        # rotation of items
        
        # translate items in the origin
        inverse_translation_matrix = get_translation_matrix(-self.pos_x, -self.pos_y, -self.pos_z)
        
        # remove rotation along y-axis
        inverse_y_rotation_matrix = get_y_rotation_matrix(-self.rot_y)
        
        # remove rotation along z-axis
        inverse_z_rotation_matrix = get_z_rotation_matrix(-self.rot_z)
        
        # rotate along x-axis
        rotation_matrix = get_x_rotation_matrix(angle)
        
        # restore rotation along z-axis
        z_rotation_matrix = get_z_rotation_matrix(self.rot_z)
        
        # restore rotation along y-axis
        y_rotation_matrix = get_y_rotation_matrix(self.rot_y)
        
        # translate back in the starting point
        translation_matrix = get_translation_matrix(self.pos_x, self.pos_y, self.pos_z)
        
        # apply transformations and rotate each single item modifying their attributes
        transformation_matrix = translation_matrix @ y_rotation_matrix @ z_rotation_matrix @ rotation_matrix @ inverse_z_rotation_matrix @ inverse_y_rotation_matrix @ inverse_translation_matrix
        for item in self.items:
            item.transform(transformation_matrix)
            item.rotate_x(angle)

    def rotate_y(self, angle):
        # rotation of center
        new_angle = self.rot_y + angle
        while new_angle >= 360: new_angle -= 360
        while new_angle < 0:    new_angle += 360
        self.rot_y = new_angle
        
        # rotation of items
        
        # translate items in the origin
        inverse_translation_matrix = get_translation_matrix(-self.pos_x, -self.pos_y, -self.pos_z)
        
        # remove rotation along x-axis
        inverse_x_rotation_matrix = get_x_rotation_matrix(-self.rot_x)
        
        # remove rotation along z-axis
        inverse_z_rotation_matrix = get_z_rotation_matrix(-self.rot_z)
        
        # rotate along y-axis
        rotation_matrix = get_y_rotation_matrix(angle)
        
        # restore rotation along z-axis
        z_rotation_matrix = get_z_rotation_matrix(self.rot_z)
        
        # restore rotation along x-axis
        x_rotation_matrix = get_x_rotation_matrix(self.rot_x)
        
        # translate back in the starting point
        translation_matrix = get_translation_matrix(self.pos_x, self.pos_y, self.pos_z)
        
        # apply transformations and rotate each single item modifying their attributes
        transformation_matrix = translation_matrix @ x_rotation_matrix @ z_rotation_matrix @ rotation_matrix @ inverse_z_rotation_matrix @ inverse_x_rotation_matrix @ inverse_translation_matrix
        for item in self.items:
            item.transform(transformation_matrix)
            item.rotate_y(angle)

    def rotate_z(self, angle):
        # rotation of center
        new_angle = self.rot_z + angle
        while new_angle >= 360: new_angle -= 360
        while new_angle < 0:    new_angle += 360
        self.rot_z = new_angle
        
        # rotation of items
        
        # translate items in the origin
        inverse_translation_matrix = get_translation_matrix(-self.pos_x, -self.pos_y, -self.pos_z)
        
        # remove rotation along x-axis
        inverse_x_rotation_matrix = get_x_rotation_matrix(-self.rot_x)
        
        # remove rotation along y-axis
        inverse_y_rotation_matrix = get_y_rotation_matrix(-self.rot_y)
        
        # rotate along z-axis
        rotation_matrix = get_z_rotation_matrix(angle)
        
        # restore rotation along y-axis
        y_rotation_matrix = get_y_rotation_matrix(self.rot_y)
        
        # restore rotation along x-axis
        x_rotation_matrix = get_x_rotation_matrix(self.rot_x)
        
        # translate back in the starting point
        translation_matrix = get_translation_matrix(self.pos_x, self.pos_y, self.pos_z)
        
        # apply transformations and rotate each single item modifying their attributes
        transformation_matrix = translation_matrix @ x_rotation_matrix @ y_rotation_matrix @ rotation_matrix @ inverse_y_rotation_matrix @ inverse_x_rotation_matrix @ inverse_translation_matrix
        for item in self.items:
            item.transform(transformation_matrix)
            item.rotate_z(angle)

    def add(self, item):
        self.items.append(item)

    def remove(self):
        pass

    def sync_instance_id(self, instance_id_counter):
        for item in self.items:
            instance_id_counter += 1
            item.instance_id = instance_id_counter
        return instance_id_counter
    
    def copy(self):
        copied_blueprint = Blueprint(self.name)
        for item in self.items:
            copied_blueprint.add(item.copy())
        return copied_blueprint
    
    def pretty_print(self):
        name_str  = self.name.ljust(20, ' ')
        pos_x_str = str(round(self.pos_x, 3)).ljust(10, ' ')
        pos_y_str = str(round(self.pos_y, 3)).ljust(10, ' ')
        pos_z_str = str(round(self.pos_z, 3)).ljust(10, ' ')
        rot_x_str = str(round(self.rot_x, 3)).ljust(10, ' ')
        rot_y_str = str(round(self.rot_y, 3)).ljust(10, ' ')
        rot_z_str = str(round(self.rot_z, 3)).ljust(10, ' ')
        
        return name_str  + \
               pos_x_str + \
               pos_y_str + \
               pos_z_str + \
               rot_x_str + \
               rot_y_str + \
               rot_z_str

    def serialize(self):
        return "{}:{}:{}:{}:{}:{}:{}".format(self.name,
                                       round(self.pos_x, 3),
                                       round(self.pos_y, 3),
                                       round(self.pos_z, 3),
                                       round(self.rot_x, 3),
                                       round(self.rot_y, 3),
                                       round(self.rot_z, 3))
    def __str__(self):
        xml_output = ""
        for item in self.items:
            xml_output += str(item)
        return xml_output