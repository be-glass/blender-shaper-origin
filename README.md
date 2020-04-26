# Blender Shaper Origin

## Description

An add-on for  [Blender](https://www.blender.org/) to:

- Create cutting shapes for [Shaper Origin](https://www.shapertools.com)
- Visualize the cuts in Blender's 3D view (with cutting depth and tool diameter)
- Export the shapes in SVG format, ready for import to the Origin.

The idea behind this plugin is to have a full model of your finished item is visible in Blender. 
This should allow to integrate the modelling for Shaper Origin with other items and/or environment, 
like Rooms, furniture, or 3D printed items, check how pars fit, 
and possibly animate functions and interactions between different items.  

This add-on is still in an early development phase. Please expect minor bugs!

## Table of Contents
  
1.  [Description](##Description)
1.  [Installation](##Installation)
1.  [Usage](##Usage)
    1. [Getting Started](##Getting Started)
    1. [Reference](##Reference)
1.  [Contributing](##Contributing)
1.  [Credits](##Credits)
1.  [License](##License)


## Installation

### Prerequisites
Blender, of course. This add-on was developed and tested on Blender v2.8.2.

### Download

- Download or clone this repository.
- In Blender
    - File > Edit > Preferences
    - Add-ons > Install
        - Choose `__init__.py` inside the the downloaded/clones repository
        - click \[Install Add-on]
    - Enable the plugin:  [x] *Mesh Shaper Origin Toolbox*
    - close the Preferences window

### Check

If the add-on is active, the properties panel (shortcut: N) will contain
  - a new tab called *'SO Cut'*. 
  - a sub-panel called *'SO Cut Seetings'* attached to the *Item* tab.
    
## Usage

### Getting Started

To get started, try a simple scene with just one shape to cut, and stay in the X-Y plane 

1. Create an object that represents a cutting shape. 

    The add-on expects a MESH or a CURVE object. The shape must be parallel to the (local) X-Y plane
    
    - A CURVE can be of type POLY, BEZIER, or NURBS. It may be open or closed. 
    
2. If you created a MESH, make sure that it contains one single N-gon face. 
    Blender can create N-gons in EDIT mode from Vertices, Edges, or co-planar faces (shortcut: F).

3. Make sure Blender is in OBJECT mode, your object is selected and go to the N-Panel. 
Go to `Item > SO Cut Settings`, and choose a *cut type*. Leave the other paramters as they are.

4. Go to N-Panel > SO Cut > Export. Set the *Export Directory*, and press `Export Cuts`. 
You will find one or several SVG files in the given directory.  

5. The SVG file(s) will be ready for import to the *Origin* (USB or cloud). 
 

### Reference

#### Collections

Different work pieces should be organized in Blender collections. 
Every work piece should contain exactly one Perimeter, and it may contain any number of other cutting shapes.
Objects inside the same collection will interact. Collection hierarchy doesn't matter.

#### Perimeter
The Perimeter defines the outline of the work piece. 
Depending on project, the Perimeter may be just a quad defining the outline of a sheet of wood, or it may be a 
complicated shape that will become the outline of the finished item. 
The visualization subtracts all active shapes in a collection from the Perimeter.

#### Orientation

Perimeters may be translated and rotated. 
The local z-axis of the Perimeter defines the axis (plunge direction) of the router tool.

All other shapes must be parallel to the perimeter in their collection.

#### Item / Cut Settings

- Cut Type

    - **None**: The shape is inactive (default)
    - **Online**: Cut along this shape, centered.
    - **Exterior**: Cut along the outside of this shape
    - **Interior**: Cut along the inside of this shape
    - **Perimeter**: Defines the outline of the actual work piece
    - **Cutout**: Like *Interior*, but adjust the cut depth to the *Perimeter* thickness
    - **Pocket**: Carve the pocket inside this shape
    - **Guide**: Just for information - don't cut anything

    Note that not all combinations are possible:
    - *Perimeter*, *Cutout*, and *Pocket* is only available for MESH.
    - Open curves can only cut *Online*.

- **Cut Depth**: used for visualization
- **Tool Diameter**: used for visualization, and dogbone fillet radius
- **Simulate Cut**: enables visualization (see next section)
- **Dogbone Fillets**: adds dogbone fillets to concave corners

#### SO Cut / Export

- **Preview**: enables a preview of all shapes to be exports. 

  - The bounding frame of the preview can be tranlated, rotated or shifted as convenient. 
    This has no effect on the exported datas. 
  
  - The addon does not attempt to arrange the relative placement of the work pieces in the exported drawing.
    When a shape is added, or the preview gets enabled, the user needs to translate the 
    representation of the perimeters along the X-Y plane of the bounding frame! 
    
- **Selected Only**: The SVG export will include only selected items. 
If disabled, all objects with a **cut type** other than `None` will be exported.

- **Export Directory**: Defines where the exported SVG file(s) will be saved. 

- **Separate Files**: If enabled, collections/objects (TBC) will be saved in different files, 
named as the collections/objects (TBC) in the Blender project. If disabled, 
all shapes are exported to one file, named as the actual Blender project.

- **Rebuild**: Rebuilding all internal objects may be useful when the project should be inconsistent, maybe after an internal object was modified or deleted manually, the add-on version changed, or in case of a bug. This button should disappear in a more mature version of the addon.

- **Export Cuts**: Converts the shapes to SVG and writes to disk.   
    
   *Origin* will be able to import the shapes and detect the *cut type* automatically.
   *Cut depths* and *Tool diameters* are included as meta data, but cannot be evaluated by *Origin.*  




## Contributing

Please don't hesitate to contribute to this add-on through the usual means and tools of Github.

This development is still in an early phase. I consider it stable enough for my own work, and to share it with others. 

At this moment, please
- do not report minor issues, that can be worked around easily.
- report major stability and usability issues  

## Credits

Thanks a lot to everybody who contributed to Blender, 
for making this incredible application and its API available to its wonderful community! 

## License

GPL3 applies. See LICENSE file in this directory.


