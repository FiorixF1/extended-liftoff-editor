# Extended Liftoff Editor

This application improves the track building for the FPV drone simulator Liftoff by letting you copy and paste complex objects composed by many basic blocks of the editor.

The ```blueprints``` folder stores the XML code for each created object plus a preview image in PNG format. The main steps to create an object, import it in ELE, create a track and export it in Liftoff are the following:
* In the Liftoff Editor, create a new map in the Drawing Board and build inside it the object you want to import in ELE. Build the object keeping in mind that the center of the map with coordinates (0, 0, 0) is used as center of rotation.
* The XML code of the built object can be found inside ```C:\Program Files\Steam\steamapps\common\Liftoff\Tracks```. Extract the content of the "blueprints" tag from it and copy it in a file inside the ```blueprints``` folder. The "blueprint" tag must also contain the XSD declaration, which is contained in the second row of the original Liftoff file (this is required for parsing XML). The copied file should have a descriptive name and the XML extension.
* Open the application by double clicking ```ele.bat``` (Windows) or ```ele.sh``` (Linux). The GUI is quite intuitive to use.
* The command "Generate XML" will create the XML code with a new "blueprint" tag that should be copied into the original Liftoff track file. After doing that, update the "lastTrackItemID" tag with the itemID of the last object in the file (otherwise the map WON'T BE SHOWN in the game).

A more detailed tutorial can be found [here](https://youtu.be/vBXRHSZm5IU).

# Requirements

This application needs Python 3 installed plus a couple of libraries (Numpy and PIL) which can be installed with the following commands:
* ```pip install numpy```
* ```pip install pillow```

