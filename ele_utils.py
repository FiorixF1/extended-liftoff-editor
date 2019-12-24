import numpy as np
from math import radians, degrees, asin, atan2
from pyquaternion import Quaternion



def rotate(object_x, object_y, object_z, center_x, center_y, center_z, q_rotation):
    q_center = Quaternion([0, center_x, center_y, center_z])
    q_object = Quaternion([0, object_x, object_y, object_z])
    q_vector = q_object - q_center
    answer = q_center + q_rotation*q_vector*q_rotation.conjugate
    return (answer.x, answer.y, answer.z)



# queste sono rotazioni fatte secondo gli assi LOCALI, cioè modificati da rotazioni successive, come succede nell'editor di liftoff
# orientation = tupla di tre quaternioni
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

# effettua tre rotazioni locali secondo tutti i tre gli assi
def l_rotate(orientation, angle_x, angle_y, angle_z):
    return l_rotate_z(l_rotate_x(l_rotate_y(orientation, angle_y), angle_x), angle_z)

# ottieni quaternione corrispondente alle tre rotazioni in successione
def l_get_quat(orientation, angle_x, angle_y, angle_z):
    quat = Quaternion(axis=[orientation[1].x, orientation[1].y, orientation[1].z], angle=radians(angle_y))
    orientation = l_rotate_y(orientation, angle_y)
    quat = Quaternion(axis=[orientation[0].x, orientation[0].y, orientation[0].z], angle=radians(angle_x))*quat
    orientation = l_rotate_x(orientation, angle_x)
    quat = Quaternion(axis=[orientation[2].x, orientation[2].y, orientation[2].z], angle=radians(angle_z))*quat
    #orientation = l_rotate_z(orientation, angle_z)
    return quat



# queste sono rotazioni fatte secondo gli assi GLOBALI, che non cambiano
# orientation = tupla di tre quaternioni
def g_rotate_x(orientation, angle):
    local_rotation = Quaternion(axis=[1, 0, 0], angle=radians(angle))
    new_y = local_rotation*orientation[1]*local_rotation.conjugate 
    new_x = local_rotation*orientation[0]*local_rotation.conjugate
    new_z = local_rotation*orientation[2]*local_rotation.conjugate
    return (new_x, new_y, new_z)

def g_rotate_y(orientation, angle):
    local_rotation = Quaternion(axis=[0, 1, 0], angle=radians(angle))
    new_y = local_rotation*orientation[1]*local_rotation.conjugate 
    new_x = local_rotation*orientation[0]*local_rotation.conjugate
    new_z = local_rotation*orientation[2]*local_rotation.conjugate
    return (new_x, new_y, new_z)

def g_rotate_z(orientation, angle):
    local_rotation = Quaternion(axis=[0, 0, 1], angle=radians(angle))
    new_y = local_rotation*orientation[1]*local_rotation.conjugate 
    new_x = local_rotation*orientation[0]*local_rotation.conjugate
    new_z = local_rotation*orientation[2]*local_rotation.conjugate
    return (new_x, new_y, new_z)

# effettua tre rotazioni globali secondo tutti i tre gli assi
def g_rotate(orientation, angle_x, angle_y, angle_z):
    return g_rotate_z(g_rotate_x(g_rotate_y(orientation, angle_y), angle_x), angle_z)

# ottieni quaternione corrispondente alle tre rotazioni in successione
def g_get_quat(orientation, angle_x, angle_y, angle_z):
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
        
        # orientamento degli assi locali
        self.quat_x = Quaternion(w=0, x=1, y=0, z=0)
        self.quat_y = Quaternion(w=0, x=0, y=1, z=0)
        self.quat_z = Quaternion(w=0, x=0, y=0, z=1)
        
        # quaternione che rappresenta la rotazione iniziale
        self.quat = None
        
        # inizializza orientamento degli assi locali e quaternione iniziale
        self._init_quat()

    # initial orientation is based on LOCAL axis
    def _init_quat(self):
        local_rotation_1 = Quaternion(axis=[self.quat_y.x, self.quat_y.y, self.quat_y.z], angle=radians(self.rot_y))
        self.quat_y = local_rotation_1*self.quat_y*local_rotation_1.conjugate 
        self.quat_x = local_rotation_1*self.quat_x*local_rotation_1.conjugate
        self.quat_z = local_rotation_1*self.quat_z*local_rotation_1.conjugate

        local_rotation_2 = Quaternion(axis=[self.quat_x.x, self.quat_x.y, self.quat_x.z], angle=radians(self.rot_x))
        self.quat_y = local_rotation_2*self.quat_y*local_rotation_2.conjugate 
        self.quat_x = local_rotation_2*self.quat_x*local_rotation_2.conjugate
        self.quat_z = local_rotation_2*self.quat_z*local_rotation_2.conjugate
 
        local_rotation_3 = Quaternion(axis=[self.quat_z.x, self.quat_z.y, self.quat_z.z], angle=radians(self.rot_z))
        self.quat_y = local_rotation_3*self.quat_y*local_rotation_3.conjugate 
        self.quat_x = local_rotation_3*self.quat_x*local_rotation_3.conjugate
        self.quat_z = local_rotation_3*self.quat_z*local_rotation_3.conjugate
        
        self.quat = local_rotation_3*local_rotation_2*local_rotation_1

    def translate(self, x, y, z):
        self.pos_x += x
        self.pos_y += y
        self.pos_z += z
    
    def rotate(self, pitch, yaw, roll):
        orientation = (Quaternion(self.quat_x), Quaternion(self.quat_y), Quaternion(self.quat_z))
        self.quat_x, self.quat_y, self.quat_z = g_rotate(orientation, pitch, yaw, roll)
        final_quat = g_get_quat(orientation, pitch, yaw, roll)*self.quat
        self.rot_x, self.rot_y, self.rot_z = self._get_pitch_yaw_roll(final_quat)
    
    def _get_pitch_yaw_roll(self, orientation):
        # given the quaternion representing all the rotations, extract the Euler angles
        # formulas taken from this WONDERFUL website
        # https://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToEuler/index.htm
        # e = +1 or -1
        # p0 = w
        # p1 = quat.y 
        # p2 = quat.x
        # p3 = quat.z
        e = -1
        p0 = orientation.w
        p1 = orientation.y
        p2 = orientation.x
        p3 = orientation.z

        b = asin(2*(p0*p2+e*p1*p3))
        if round(degrees(b), 5) == 90 or round(degrees(b), 5) == -90:
            c = 0
            a = atan2(p1, p0)
        else:
            a = atan2(2*(p0*p1 - e*p2*p3), 1-2*(p1**2+p2**2))
            c = atan2(2*(p0*p3 - e*p1*p2), 1-2*(p2**2+p3**2))
        return (round(degrees(b), 5), round(degrees(a), 5), round(degrees(c), 5))

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
            new_position = rotate(item.pos_x, item.pos_y, item.pos_z, self.pos_x, self.pos_y, self.pos_z, rotation)
            item.pos_x = new_position[0]
            item.pos_y = new_position[1]
            item.pos_z = new_position[2]

    def _rotate_y(self, angle):
        rotation = Quaternion(axis=[0, 1, 0], angle=radians(angle))
        
        # rotation of center
        self.rot_y = (self.rot_y + angle) % 360
        # translation of items
        for item in self.items:
            new_position = rotate(item.pos_x, item.pos_y, item.pos_z, self.pos_x, self.pos_y, self.pos_z, rotation)
            item.pos_x = new_position[0]
            item.pos_y = new_position[1]
            item.pos_z = new_position[2]

    def _rotate_z(self, angle):
        rotation = Quaternion(axis=[0, 0, 1], angle=radians(angle))
        
        # rotation of center
        self.rot_z = (self.rot_z + angle) % 360
        # translation of items
        for item in self.items:
            new_position = rotate(item.pos_x, item.pos_y, item.pos_z, self.pos_x, self.pos_y, self.pos_z, rotation)
            item.pos_x = new_position[0]
            item.pos_y = new_position[1]
            item.pos_z = new_position[2]

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
