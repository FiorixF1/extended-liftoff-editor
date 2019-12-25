import numpy as np
from math import radians, degrees, asin, atan2
from pyquaternion import Quaternion



# apply arbitrary rotation on a point using a quaternion
# @param object = coordinates of the object to rotate
# @param center = coordinates of the center of rotation
# @param q_rotation = the rotation expressed as a quaternion
# @return coordinates of the rotated object
def rotate(object_x, object_y, object_z, center_x, center_y, center_z, q_rotation):
    q_center = Quaternion([0, center_x, center_y, center_z])
    q_object = Quaternion([0, object_x, object_y, object_z])
    q_vector = q_object - q_center
    answer = q_center + q_rotation*q_vector*q_rotation.conjugate
    return (answer.x, answer.y, answer.z)



# these functions apply rotations to the local axis along the LOCAL axis themselves, which are modified by previous rotations, as it happens in the Liftoff Editor
# @param orientation = a tuple of three quaternions representing the local axis
# @return a tuple of three quaternions representing the new rotated local axis
def l_rotate_x(orientation, angle):
    local_rotation = Quaternion(axis=[orientation[0].x, orientation[0].y, orientation[0].z], angle=radians(angle))
    new_y = local_rotation*orientation[1]*local_rotation.conjugate 
    new_x = local_rotation*orientation[0]*local_rotation.conjugate
    new_z = local_rotation*orientation[2]*local_rotation.conjugate
    return (new_x, new_y, new_z)

def l_rotate_y(orientation, angle):
    local_rotation = Quaternion(axis=[orientation[1].x, orientation[1].y, orientation[1].z], angle=radians(angle))
    new_y = local_rotation*orientation[1]*local_rotation.conjugate 
    new_x = local_rotation*orientation[0]*local_rotation.conjugate
    new_z = local_rotation*orientation[2]*local_rotation.conjugate
    return (new_x, new_y, new_z)

def l_rotate_z(orientation, angle):
    local_rotation = Quaternion(axis=[orientation[2].x, orientation[2].y, orientation[2].z], angle=radians(angle))
    new_y = local_rotation*orientation[1]*local_rotation.conjugate 
    new_x = local_rotation*orientation[0]*local_rotation.conjugate
    new_z = local_rotation*orientation[2]*local_rotation.conjugate
    return (new_x, new_y, new_z)

# apply three local rotations along all three axis (order is YXZ)
def l_rotate(orientation, angle_x, angle_y, angle_z):
    return l_rotate_z(l_rotate_x(l_rotate_y(orientation, angle_y), angle_x), angle_z)

# get quaternion corresponding to the local rotation along all three axis (order is YXZ)
def l_get_quat(orientation, angle_x, angle_y, angle_z):
    quat = Quaternion(axis=[orientation[1].x, orientation[1].y, orientation[1].z], angle=radians(angle_y))
    orientation = l_rotate_y(orientation, angle_y)
    quat = Quaternion(axis=[orientation[0].x, orientation[0].y, orientation[0].z], angle=radians(angle_x))*quat
    orientation = l_rotate_x(orientation, angle_x)
    quat = Quaternion(axis=[orientation[2].x, orientation[2].y, orientation[2].z], angle=radians(angle_z))*quat
    return quat



# these functions apply rotations to the local axis along the GLOBAL axis, which are fixed
# @param orientation = a tuple of three quaternions representing the local axis
# @return a tuple of three quaternions representing the new rotated local axis
def g_rotate_x(orientation, angle):
    global_rotation = Quaternion(axis=[1, 0, 0], angle=radians(angle))
    new_y = global_rotation*orientation[1]*global_rotation.conjugate 
    new_x = global_rotation*orientation[0]*global_rotation.conjugate
    new_z = global_rotation*orientation[2]*global_rotation.conjugate
    return (new_x, new_y, new_z)

def g_rotate_y(orientation, angle):
    global_rotation = Quaternion(axis=[0, 1, 0], angle=radians(angle))
    new_y = global_rotation*orientation[1]*global_rotation.conjugate 
    new_x = global_rotation*orientation[0]*global_rotation.conjugate
    new_z = global_rotation*orientation[2]*global_rotation.conjugate
    return (new_x, new_y, new_z)

def g_rotate_z(orientation, angle):
    global_rotation = Quaternion(axis=[0, 0, 1], angle=radians(angle))
    new_y = global_rotation*orientation[1]*global_rotation.conjugate 
    new_x = global_rotation*orientation[0]*global_rotation.conjugate
    new_z = global_rotation*orientation[2]*global_rotation.conjugate
    return (new_x, new_y, new_z)

# apply three global rotations along all three axis (order is YXZ)
def g_rotate(orientation, angle_x, angle_y, angle_z):
    return g_rotate_z(g_rotate_x(g_rotate_y(orientation, angle_y), angle_x), angle_z)

# get quaternion corresponding to the global rotation along all three axis (order is YXZ)
def g_get_quat(angle_x, angle_y, angle_z):
    quat = Quaternion(axis=[0, 1, 0], angle=radians(angle_y))
    quat = Quaternion(axis=[1, 0, 0], angle=radians(angle_x))*quat
    quat = Quaternion(axis=[0, 0, 1], angle=radians(angle_z))*quat
    return quat



class Item:
    def __init__(self, item_id, instance_id, pos_x, pos_y, pos_z, rot_x, rot_y, rot_z):
        self.item_id = item_id
        self.instance_id = instance_id

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = pos_z
        
        self.rot_x = rot_x
        self.rot_y = rot_y
        self.rot_z = rot_z
        
        # orientation of the local axis
        self.orientation = ( Quaternion(w=0, x=1, y=0, z=0),
                             Quaternion(w=0, x=0, y=1, z=0),
                             Quaternion(w=0, x=0, y=0, z=1) )
        
        # quaternion representing the initial rotation
        self.quat = None
        
        # initialize the orientation of the local axis and the initial quaternion
        self._init_quat()

    # initial orientation is based on LOCAL axis
    def _init_quat(self):
        new_orientation = l_rotate(self.orientation, self.rot_x, self.rot_y, self.rot_z)
        new_quat = l_get_quat(self.orientation, self.rot_x, self.rot_y, self.rot_z)
        
        self.orientation = new_orientation
        self.quat = new_quat

    def translate(self, x, y, z):
        self.pos_x += x
        self.pos_y += y
        self.pos_z += z
    
    def rotate(self, pitch, yaw, roll):
        self.orientation = g_rotate(self.orientation, pitch, yaw, roll)
        # final_quat is the product of two rotations:
        # - the initial one when the item is placed inside the blueprint
        # - the last one when the blueprint itself is rotated in the world
        final_quat = g_get_quat(pitch, yaw, roll)*self.quat
        self.rot_x, self.rot_y, self.rot_z = self._get_pitch_yaw_roll(final_quat)
    
    def _get_pitch_yaw_roll(self, quaternion):
        # given a quaternion representing all the rotations, extract the Euler angles
        # formulas are taken from this WONDERFUL website
        # https://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToEuler/index.htm
        e = -1
        p0 = quaternion.w
        p1 = quaternion.y
        p2 = quaternion.x
        p3 = quaternion.z

        pitch = asin(2*(p0*p2 + e*p1*p3))
        yaw   = atan2(2*(p0*p1 - e*p2*p3), 1-2*(p1**2 + p2**2))
        roll  = atan2(2*(p0*p3 - e*p1*p2), 1-2*(p2**2 + p3**2))
        
        pitch = round(degrees(pitch), 6)
        yaw   = round(degrees(yaw), 6)
        roll  = round(degrees(roll), 6)
        
        return (pitch, yaw, roll)

    def copy(self):
        return Item(self.item_id, self.instance_id, self.pos_x, self.pos_y, self.pos_z, self.rot_x, self.rot_y, self.rot_z)

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
                                                  round(self.pos_x, 3),
                                                  round(self.pos_y, 3),
                                                  round(self.pos_z, 3),
                                                  round(self.rot_x, 3),
                                                  round(self.rot_y, 3),
                                                  round(self.rot_z, 3))



# CONVENTION USED IN LIFTOFF:
# - x positive right
# - y positive up
# - z positive forward -> left-handed coordinate system
# - pitch is the rotation along x
# - yaw   is the rotation along y
# - roll  is the rotation along z
# - rotation positive clockwise
# - order of rotation is YXZ
# This program applies rotations with regards to the global (fixed) XYZ axis,
# while the Editor rotates the objects with regards to their local (moving) XYZ axis.
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
        for item in self.items:
            item.translate(x, y, z)

    def rotate(self, pitch, yaw, roll):
        # this rotation is actually a translation of the center of each item
        self._rotate_y(yaw)
        self._rotate_x(pitch)
        self._rotate_z(roll)
        # here comes the real rotation, the toughest part of the program
        for item in self.items:
            item.rotate(pitch, yaw, roll)

    def _rotate_x(self, angle):
        rotation = Quaternion(axis=[1, 0, 0], angle=radians(angle))
        
        # rotation of center
        self.rot_x = (self.rot_x + angle) % 360
        # translation of items
        for item in self.items:
            item.pos_x, item.pos_y, item.pos_z = rotate(item.pos_x, item.pos_y, item.pos_z,
                                                        self.pos_x, self.pos_y, self.pos_z,
                                                        rotation)

    def _rotate_y(self, angle):
        rotation = Quaternion(axis=[0, 1, 0], angle=radians(angle))
        
        # rotation of center
        self.rot_y = (self.rot_y + angle) % 360
        # translation of items
        for item in self.items:
            item.pos_x, item.pos_y, item.pos_z = rotate(item.pos_x, item.pos_y, item.pos_z,
                                                        self.pos_x, self.pos_y, self.pos_z,
                                                        rotation)

    def _rotate_z(self, angle):
        rotation = Quaternion(axis=[0, 0, 1], angle=radians(angle))
        
        # rotation of center
        self.rot_z = (self.rot_z + angle) % 360
        # translation of items
        for item in self.items:
            item.pos_x, item.pos_y, item.pos_z = rotate(item.pos_x, item.pos_y, item.pos_z,
                                                        self.pos_x, self.pos_y, self.pos_z,
                                                        rotation)

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
