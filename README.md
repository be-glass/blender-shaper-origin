# Blender Shaper Origin

## Description

An add-on for  [Blender](https://www.blender.org/) to:

- Create cutting shapes for [Shaper Origin](https://www.shapertools.com)
- Visualize the cuts in Blender's 3D view (with cutting depth and tool diameter)
- Export the shapes in SVG format, ready for import to the Origin.

The idea is to have a full model of your finished item available in Blender. 
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

### Install Add-on

- In Blender
    - File > Edit > Preferences
    - Add-ons > Install
        - Choose 
          - the downloaded zip file, *or* 
          - `__init__.py` inside cloned repository
        - click \[Install Add-on]
        
      ![install addon in blender](doc/img/install.jpg?raw=true "Addon Dialog - install")
    
    - Enable the plugin:  [x] *Mesh Shaper Origin Toolbox*
    
      ![enable addon in blender](doc/img/enable.jpg?raw=true "Addon Dialog - enable")
    
    - close the Preferences window



### Check

If the add-on is active, the properties panel (shortcut: N) will contain

  - a new tab called *'SO Cut'*. 
  - a sub-panel called *'SO Cut Seetings'* attached to the *Item* tab.

    ![n-panel](doc/img/n-panel.jpg?raw=true "N-Panel")

    
## Usage

### Getting Started

To get started, try a simple scene with just one shape to cut, and stay in the X-Y plane 

1. Create an object that represents a cutting shape. 

    The add-on expects a MESH or a CURVE object. The shape must be parallel to the (local) X-Y plane
    
    - CURVEs can be of type POLY, BEZIER, or NURBS. It may be open or closed. 
    
     ![n-gon](doc/img/ngon.jpg?raw=true "Ngon")
    
    - MESHes should contain only one single N-gon face. 
      Blender can create N-gons in EDIT mode from Vertices, Edges, or co-planar faces (shortcut: F).

2. Make sure Blender is in OBJECT mode, your object is selected and go to the N-Panel. 
Go to `Item > SO Cut Settings`, and choose a *cut type*. Leave the other paramters as they are.

     ![cutout](doc/img/cutout.jpg?raw=true "cut example")
     
     Concave corners will be rounded off by the routing bit. 
     The rounding is visible in the 3D view, but will not be exported to the SVG file.
     If selected, concave corners are extended with dogbone fillets. They are both, visible and exported. 
     
     ![dogbone](doc/img/dogbone.jpg?raw=true "dogbone example")

3. Go to N-Panel > SO Cut > Export. Set the *Export Directory*, and press `Export Cuts`. 
You find one or several SVG files in the given directory.  

     ![svg](doc/img/cutout_svg.jpg?raw=true "cutout as SVG")

4. The SVG file(s) are ready for import to the *Origin* (USB or cloud). 
 

### Reference

#### Collections

The blender project may contain more than one work pieces. Each of them needs to be organized in separate collection.
Each collection should contain exactly one Perimeter, and it may contain any number of other cutting shapes.
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

### Example

   ![example 1.1](doc/img/example1.1.jpg?raw=true "box1")

   ![example 1.2](doc/img/example1.2.jpg?raw=true "box1")

   ![example 1.3](doc/img/example1.3.jpg?raw=true "box1")

   ![example 1.4](doc/img/example1.4.jpg?raw=true "box1")

   ![example 1.5](doc/img/example1.5.jpg?raw=true "box1")

## Contributing

Please don't hesitate to contribute to this add-on through the usual means and tools of Github.

This development is still in an early phase. I consider it stable enough for my own work, and to begin sharing it with others. 

Please report major issues with functionality, stability and usability.   

## Credits

Thanks a lot to everybody who contributed to Blender, 
for making this incredible application and its API available to its wonderful community! 

## License

GPL3 applies. See LICENSE file in this directory.


