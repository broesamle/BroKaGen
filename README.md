
Br:oKaGen - The Br:osamle Katalog Generator
===========================================
Organise texts, image content, list/item-centred information
(such as publications list, curriculum vita, exhibitions, talks, etc.)
into a coherent and pleasant form for screen, presentation, print.

+ Static HTML Generator
+ Purely based on HTML, (inline) SVG, CSS
+ Articles are registered in (multiple) rubriques
+ Rubriques allow for specific spatial graphic elements and styling
+ An overall Catalogue/Main index is generated...
+ ... as well as sub-catalogues for each rubrique
+ Efficient visual and hyperlink access via the margin of the main catalogue

Recently I have been using the generator as a substitute for Keynote/Powerpoint-Type of presentation systems:
+ platform independent firm integration with web content
+ more structured and, at the same time, flexible presentation style

Usage
-----

### bash/linux

Make the root directory of your web project the current working directory.

It has to contain these python files which define the configuration.

```
CFG_ContentStructure.py
CFG_FilesPaths.py
CFG_ImageContent.py
CFG_StyleDefs.py
CFG_TemplateDefs.py
```

TODO: If they are not present it will just throw an exception without further message. (We could use some explicit config file format which we read into python structures; alternatively, at least it could catch the exception and say something nice.)

`python3 -m BroKaGen.generateKatalog -p` for processing images

`python3 -m BroKaGen.generateKatalog --help` for help (only works in a project directory with the `CFG_*.py` files which is certainly not ideal (see above).



Install
-------

### Ubuntu 16.04

*WARNING!* These instructions are incomplete!

`pip3 install pillow`

`pip3 install markdown`

`sudo apt-get install libjpeg-dev`

somewhere in the python module path clone/place the following packages:

`git clone https://github.com/broesamle/BroKaGen.git`

`git clone https://github.com/broesamle/PyBroeModules.git`

### Windows (10)

Assuming there is a python3 already installed and the interpreter is added to the path.

add `C:\Users\<USER>\local\lib\python3\site-packages\BroKaGen` to PYTHONPATH

(Replace <USER> with your user directory)

`git clone https://github.com/broesamle/BroKaGen.git`

`git clone https://github.com/broesamle/PyBroeModules.git`

as Administrator:

`python -m pip install markdown`

`python -m pip install pillow`

ToDos and Open Ends
-------------------
 ... it's more work-in-progress-ish than settled

### Create a Template Project

Currently, only the engine is in the repo...

Making a presentation will at some point become more straight forward based on suitable templates:

1. Checkout the generator
2. Adapt the template `CFG_*` files appropriately (Rubriques, Icons)
3. Define Logo

### Clean logging
There should be logging levels so that warnings (i.e. about ignored input files) can be read separately from more general infos.
