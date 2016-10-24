import os, io, codecs, re, datetime
from string import Template

try:
    import PIL
    import PIL.Image
    pilOK = True
except ImportError:
    print ("WARNING: PIL not Installed!")
    pilOK = False

import xml.etree.ElementTree as ET
import markdown

import PyBroeModules.ItemsCollectionA as IC
from PyBroeModules.StripNamespace import stripNamespace

from CFG_FilesPaths import indexHTMLwww, indexHTMLlocal

def writeHTMLfile(outFN,documentHTML):
    print ("HTML-OUT:",outFN)
    localDir,filename = os.path.split(outFN)
    os.makedirs(localDir,exist_ok=True)

    output_file = codecs.open(outFN, "w", encoding="utf-8", errors="xmlcharrefreplace")
    output_file.write(documentHTML)
    output_file.close()


class RubriqueSet(IC.ItemsCollection):
    def __init__(self):
        IC.ItemsCollection.__init__(self,defaults={'rubriqueNom':"DEFAULTNAME"})

    def readSVGContent (self,filename,prefix="ico-",accesKey="iconsvg"):
        ns = {'svg':'http://www.w3.org/2000/svg', 'xlink':"http://www.w3.org/1999/xlink"}

        tree = ET.parse(filename)
        root = tree.getroot()

        viewbox = root.get('viewBox',"0,0,10,10")
        elementXpath = "svg:g[@id]"
        for el in root.findall(elementXpath, ns):
            print ("SVG element", el.attrib['id'])

            if el.attrib['id'][:len(prefix)] == prefix:
                key = el.attrib['id'][len(prefix):]
                if key not in self:
                    print ("Warning. Icon for non-existing rubrique: %s" % key)
                else:
                    s = io.StringIO()
                    ET.ElementTree(el).write(s,encoding="unicode")
                    self[ key ] [accesKey] = stripNamespace(s.getvalue())
        return viewbox

class ArticlesCollection(IC.FilesInputCollection):
    def __init__(self,debugoutoputDIR="",defaults={'title':"",'subtitle':"",'comment':"",'author':"",'date':"",'vitadate':"",'rubriques':[]},**kwargs):
        self.relativeHRefs = set()

        self.md = markdown.Markdown(extensions = ['markdown.extensions.meta'])
        if not debugoutoputDIR:     self.debug = False
        else:                       self.debug = True
        IC.FilesCollection.__init__(self,defaults=defaults,reverse=True,**kwargs)
        #self.rubriques = rubriques


    def processInput(self,key=None,text=""):
        html =  self.md.reset().convert(text)
        try:
            self.addItem(key,self.md.Meta)
        except Exception as e:
            print ("key of file with empty meta info (or the like):",key)
            raise e

        if 'rubriques' not in self[key]: self[key]['rubriques'] = []

        self[key]['rubriques'] = list(filter(lambda x:x!='',self[key]['rubriques']))
        self[key]['content'] = html.strip()
        ### generate relative HRef, path, filename for later use
        m = re.match("(\d\d\d\d)\w?_?(.*)",key)
        if m:
            relativeDIRwww = m.groups()[0] +'/'+ m.groups()[1].replace(".mdtxt","").replace(".auto","")
            relativeHRef = relativeDIRwww + '/' + indexHTMLwww
            localDIRrel = os.path.join( m.groups()[0], m.groups()[1].replace(".mdtxt","").replace(".auto","") )
            print ("KEY->LOCALHREF:",key, relativeHRef)
            self[key]['relativeDIRwww'] = relativeDIRwww
            self[key]['relativeHRef'] = relativeHRef
            self[key]['localDIRrel'] = localDIRrel
            self[key]['localFILErel'] = os.path.join(localDIRrel, indexHTMLlocal)

        else:
            raise ValueError("Failed to transform filename into valid local reference: "+key)

        if self[key]['relativeHRef'] in self.relativeHRefs:
            raise ValueError("Duplicate Local HReference: ", key, self[key]['relativeHRef'])

        self.relativeHRefs.add(self[key]['relativeHRef'])

    def detectDates(self):
        for key in self.keys():
            try:
                self[key]['year'],self[key]['month'],self[key]['day'] = [ str(x) for x in re.match("(\d\d\d\d)-?(\d?\d)?-?(\d?\d)?",self[key]['date']).groups() ]
                print (key, "DATE:",self[key]['date'], ":", self[key]['year'], self[key]['month'], self[key]['day'])
                if self[key]['year'] == 'None': self[key]['year'] = ""
                if self[key]['month'] == 'None': self[key]['month'] = ""
                if self[key]['day'] == 'None': self[key]['day'] = ""
                try:    self[key]['monthname'] = datetime.date(1901,int(self[key]['month']),1).strftime("%b")
                except: self[key]['monthname'] = ""
            except Exception as e:
                self[key]['year'],self[key]['month'],self[key]['day'] = "","",""
                print ( "WARNING: Date not detected. %s in %s." % (self[key]['date'],key) )
                print ( e )

            if self[key]['vitadate'] == 'None': self[key]['vitadate'] = ''


class ImageCollection(IC.FilesCollection):
    def __init__(self, projectRootDIRabs, imageRootDIRrel, htmlRootDIRrel,
            thisseriesDIRrel="",
            title="TITEL DER SERIE",
            htmlExt="html",
            pattern="*.jpg",defaults = {'title':"",'subtitle':"",'author':"",'date':""},
            maxsizes={'full':(1000,1000),'medium':(1000,600),'thumb':(1000,240)},
            **kwargs):
        self.maxsizes=maxsizes
        self.projectRootDIRabs=projectRootDIRabs
        self.imageRootDIRrel=imageRootDIRrel
        self.htmlRootDIRrel=htmlRootDIRrel
        self.thisseriesDIRrel=thisseriesDIRrel
        self.title = title
        self.htmlExt = htmlExt
        IC.FilesCollection.__init__(self,
            inputDIR=os.path.join(projectRootDIRabs,imageRootDIRrel,thisseriesDIRrel),
            defaults=defaults,
            pattern=pattern,**kwargs)

    def processFile(self,key,filepath,filename):
        inFN = os.path.join(filepath,filename)
        ext = os.path.splitext(filename)[1][1:]
        self.addItem(key,{'inFN':inFN, 'file_extension':ext, 'htmlFN':self.getHtmlFN(key)})
        for sizekey in self.maxsizes:
            self[key]['imageFN_%s'%sizekey] = self.getImageFN(key,sizekey)

    def generateSlideshowHTMLfiles(self,imageviewTEM,htmlTargetDIRrel,relativeRootHRef,addFields={},slideshowSelection=None):
        if slideshowSelection:  items2process = slideshowSelection
        else:                   items2process = list(self.keys())
        #print ("generateSlideshowHTMLfiles", items2process)

        this = items2process[-1]
        next = items2process[0]
        counter = 0
        for key in items2process[1:]:
            counter+=1
            prev = this
            this = next
            next = key
            documentdict = {'title':(self.title+str(counter)+'/'+str(len(items2process))),'THIS_ELEMENT_KEY':this,'subtitle':"",'date':""}
            print ("    image:", self.getHtmlFN(documentdict['THIS_ELEMENT_KEY']))
            documentHTML = imageviewTEM.substitute(
                self[this],
                nextImageHref=self.getHtmlFN(next),
                previousImageHref=self.getHtmlFN(prev),
                relativeRootHRef=relativeRootHRef,
                imagesource=os.path.join(relativeRootHRef,self.imageRootDIRrel,self.getImageFN(this,'full')).replace("\\","/"),
                **addFields)

            absoluteFilename = os.path.join(
                self.projectRootDIRabs,
                self.htmlRootDIRrel.replace("\\","/"),
                htmlTargetDIRrel,
                self.getHtmlFN(documentdict['THIS_ELEMENT_KEY']))
            print ( "writing image series file" + absoluteFilename )
            writeHTMLfile ( absoluteFilename , documentHTML )

        counter+=1
        prev = this
        this = next
        next = items2process[0]
        documentdict = {'title':(self.title+str(counter)+'/'+str(len(items2process))),'THIS_ELEMENT_KEY':this,'subtitle':"",'date':""}
        print ("    image:", self.getHtmlFN(documentdict['THIS_ELEMENT_KEY']))
        documentHTML = imageviewTEM.substitute(
            self[this],
            nextImageHref=self.getHtmlFN(next),
            previousImageHref=self.getHtmlFN(prev),
            backlinkContent="BACK",
            relativeRootHRef=relativeRootHRef,
            imagesource=os.path.join(relativeRootHRef,self.imageRootDIRrel,self.getImageFN(this,'full')).replace("\\","/"),
            **addFields)
        writeHTMLfile ( os.path.join(self.projectRootDIRabs,self.htmlRootDIRrel,htmlTargetDIRrel,self.getHtmlFN(documentdict['THIS_ELEMENT_KEY'])), documentHTML )

    def getImageFN (self,key,sizekey):
        return "%s_%s.%s" % (key,sizekey,self[key]['file_extension'])

    def getHtmlFN (self,key):
        return key+'.'+self.htmlExt

    def generateImageFiles(self,pattern=""):
        """ Pattern currently unused."""
        if pilOK:
            outPath = os.path.join(self.projectRootDIRabs,self.htmlRootDIRrel,self.imageRootDIRrel)
            if not os.path.exists(outPath):
                os.makedirs(outPath)
            for key,dict in self.items():
                #if self.getImageFN(key,sizekey)
                for (sizekey,maxsize) in self.maxsizes.items():
                    outFN = os.path.join(outPath,self.getImageFN(key,sizekey))
                    im = PIL.Image.open(self[key]['inFN'])
                    im.thumbnail(maxsize, PIL.Image.ANTIALIAS)
                    im.save(outFN,quality=90, optimize=True, progressive=True)
        else:
            print ("WARNING: PIL not Installed; Images not converted")


class Gallery(dict):
    """ Basically a dictionary of imagecollections with some useful paths and presets defined when creating an instance."""

    def __init__(self,projectRootDIRabs,imageRootDIRrel,htmlRootDIRrel):
        self.projectRootDIRabs  = projectRootDIRabs
        self.imageRootDIRrel    = imageRootDIRrel
        self.htmlRootDIRrel     = htmlRootDIRrel

    def addImageCollection(self,key,pattern,path=""):
        """ Quick shorthand for creating an image series with the given configuration."""
        self[key] = ImageCollection(
            projectRootDIRabs   = self.projectRootDIRabs,
            imageRootDIRrel     = self.imageRootDIRrel,
            htmlRootDIRrel      = self.htmlRootDIRrel,
            thisseriesDIRrel    = path,
            pattern=pattern)
