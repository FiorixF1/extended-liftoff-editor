import ele_program



print("Loading models...")

program = ele_program.Program()
program.init()

print("Done")



def list_blueprints():
    for name in program.blueprints:
        print("--- {}".format(name))

def add_instance():
    print("Add an instance by typing n:x:y:z:p:y:r where")
    print("\tn is the name of the blueprint")
    print("\tx is the x-coordinate")
    print("\ty is the y-coordinate")
    print("\tz is the z-coordinate")
    print("\tp is the pitch angle in degrees")
    print("\ty is the yaw angle in degrees")
    print("\tr is the roll angle in degrees")
    values = input("> ").split(':')
        
    if len(values) != 7:
        print("Invalid syntax")
        return
        
    try:
        name = values[0]
        x, y, z, pitch, yaw, roll = map(lambda x: float(x), values[1:])
    except ValueError:
        print("Coordinates and angles must be float")
        return
        
    try:
        program.add_instance(name, x, y, z, pitch, yaw, roll)
        print("Done")
    except KeyError as e:
        print("Blueprint {} does not exist".format(e))    

def remove_instance():
    if len(program.instances) == 0:
        print("There are no instances to remove")
        return

    try:
        print("Specify the index of the instance to remove")
        index = input("> ")
        index = int(index)
        program.remove_instance(index)
        print("Done")
    except:
        print("Invalid index")

def show_instances():
    if len(program.instances) == 0:
        print("There are no instances to show")
        return

    print("                        X         Y         Z         Pitch     Yaw       Roll      ")
    for i in range(len(program.instances)):
        print("{} - {}".format(i, program.instances[i].pretty_print()))

def set_instance_counter():
    try:
        value = int(input("> "))
        if value < 0: raise ValueError
        program.instance_id_counter = value
        print("Done")
    except:
        print("Value must be a positive integer")

def load_project():
    try:
        program.load_project("project.dat")
        print("Project loaded")
    except FileNotFoundError:
        print("The file 'project.dat' does not exist")
    except KeyError as e:
        print("The file contains a non existing blueprint '{}'".format(e))
    except ValueError:
        print("The file contains invalid values for coordinates and angles")

def save_project():
    program.save_project(open("project.dat", "w"))
    print("Project saved into 'project.dat'")

def generate_xml():
    program.generate_xml(open("track.xml", "w"))
    print("Track saved into 'track.xml'")

def quit():
    exit()

commands = [list_blueprints,
            add_instance,
            remove_instance,
            show_instances,
            set_instance_counter,
            load_project,
            save_project,
            generate_xml,
            quit]

print()
print("Welcome to the Extended Liftoff Editor!")

while True:
    print()
    print("1 - List available blueprints")
    print("2 - Add instance")
    print("3 - Remove instance")
    print("4 - Show instances")
    print("5 - Set instance counter")
    print("6 - Load project")
    print("7 - Save project")
    print("8 - Generate XML")
    print("9 - Quit")
    
    try:
        prompt = int(input("> "))
    except:
        continue
    
    if prompt > 0 and prompt <= 9:
        commands[int(prompt)-1]()
