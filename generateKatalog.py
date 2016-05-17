import os, codecs, time, shutil, re, fnmatch
from sys import argv
	
from string import Template
import MultiTemplateA as MT

from BroKaGen import ArticlesCollection, writeHTMLfile

import CFG_TemplateDefs as TEM
import CFG_StyleDefs as CSS	
import CFG_FilesPaths as PATHS
import CFG_ImageContent as IMG
import CFG_ContentStructure as CONTSTRUCT

import argparse

parser = argparse.ArgumentParser(description='...')
parser.add_argument('-p','--processimages', action='store_true', help='proess the images (generate thumbs etc.)', default=False)
parser.add_argument('-f','--filterimages', type=str, default="", help='proess only images that match the pattern')
parser.add_argument('-a','--articlesclear', action='store_true', help='clear intermediate articles dir', default=False)
parser.add_argument('-t','--targetclear', action='store_true', help='clear the entire target output dir', default=False)

ARGS = parser.parse_args()

##########################################
### central File / Directory Configuration
##########################################
contentDIRabs 				= os.path.abspath ( os.path.join(PATHS.rootDIR,PATHS.contentDIR) )
intermediate_mdtxtDIRabs 	= os.path.abspath ( os.path.join(PATHS.rootDIR,PATHS.intermediate_mdtxtDIR) )
targetDIRabs 				= os.path.abspath ( os.path.join(PATHS.rootDIR,PATHS.targetDIR) )
imagetargetDIRabs 			= os.path.abspath ( os.path.join(targetDIRabs,PATHS.imagetargetDIR) )
documentstargetDIRabs 				= os.path.abspath ( os.path.join(PATHS.rootDIR,PATHS.targetDIR,PATHS.documntsDIR) )

print ("PATH SETTINGS:")
print ("Content Input:	                ",contentDIRabs 			)
print ("Intermediate Articles (*.mdtxt) ",intermediate_mdtxtDIRabs 	)
print ("Target WWW (*.html,...)         ",targetDIRabs 				)
print ("Target images                   ",imagetargetDIRabs 		)
print ("Target Documents (non-html)     ",documentstargetDIRabs 	)


if contentDIRabs == intermediate_mdtxtDIRabs:
	raise ValueError(
		"Article *.mdtxt (intermediate) directory must be different from content (source) directory. Current Setting: "
		+contentDIRabs+" AND "+intermediate_mdtxtDIRabs)


### clear directories if needed		
if ARGS.articlesclear: shutil.rmtree(intermediate_mdtxtDIRabs, ignore_errors=True)
if ARGS.targetclear: shutil.rmtree(targetDIRabs, ignore_errors=True)

os.makedirs(intermediate_mdtxtDIRabs,exist_ok=True)
os.makedirs(targetDIRabs,exist_ok=True)
os.makedirs(imagetargetDIRabs,exist_ok=True)
os.makedirs(documentstargetDIRabs,exist_ok=True)

PATHS.debugHTML = "debugHTML"
PATHS.markdownEXT = "mdtxt"
PATHS.markdownBatchEXT = "mdbatch"
PATHS.splitmarkdownSUFFIX = '.auto'
PATHS.htmlEXT = "html"
#PATHS.iconsFN = "Icons_current.svg"
PATHS.iconsFN = "Icons_neu.svg"


###########
### CSS ###
###########
#XSmaxwidth = 750
#fixedneedleoffset = 29.5

rubriquespecCSS_XS = ""
rubriquespecCSS_M = ""
for k in CONTSTRUCT.rubriques.keys():
	CONTSTRUCT.rubriques[k]['vPosNeutral']		= str(CONTSTRUCT.rubriques[k]['vPosBase'])+'%'
	rubriquespecCSS_XS += ".indicatorpos_%s { left:%d%%; }\n" % ( CONTSTRUCT.rubriques[k]['THIS_ELEMENT_KEY'] , CONTSTRUCT.rubriques[k]['vPosBase']*100) 
	rubriquespecCSS_M +=  ".element-as-indicator_%s { margin-left:%d%%; }\n" % ( CONTSTRUCT.rubriques[k]['THIS_ELEMENT_KEY'] , CONTSTRUCT.rubriques[k]['vPosBase']*100) 
		
rubriquespecCSS = rubriquespecCSS_XS
rubriquespecCSS += "\n@media ($Mmediaquery) { \n" + rubriquespecCSS_M + "\n}"

styleCSS = Template(CSS.main).safe_substitute(CSS.params,rubriquespecCSS=rubriquespecCSS)
styleCSS = Template(styleCSS).substitute(CSS.params)

outFN = os.path.join(targetDIRabs,"style.css")
output_file = codecs.open(outFN, "w", encoding="utf-8", errors="xmlcharrefreplace")
output_file.write(styleCSS)
output_file.close()

styleCSS = Template(CSS.startseite).substitute(CSS.params)
outFN = os.path.join(targetDIRabs,"start.css")
output_file = codecs.open(outFN, "w", encoding="utf-8", errors="xmlcharrefreplace")
output_file.write(styleCSS)
output_file.close()
	
globalVar = {}
globalVar['iconviewbox'] = CONTSTRUCT.rubriques.readSVGContent(os.path.join(contentDIRabs,PATHS.iconsFN),prefix="ico-",accesKey="iconsvg")
globalVar['generationDate'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
globalVar['BroKaGen_Version'] = "0.1"
globalVar['BroKaGen_Reference'] = 'This page was generated using <a href="https://github.com/broesamle/BroKaGen" target="_blank">Br:oKaGen</a>, Brösamle Katalog Generator.'
globalVar['indexHTML'] = PATHS.indexHTMLwww

################################
#########  Multifiles  #########
################################

print ("Processing Content...")
for filename in os.listdir(contentDIRabs):
	if fnmatch.fnmatch(filename,"*."+PATHS.markdownBatchEXT):
		print("MDBATCH:", filename)
		fullfilepath = os.path.join(contentDIRabs,filename)
		file = codecs.open(fullfilepath, mode="r", encoding="utf-8")
		batch = file.read()
		file.close()
		snippets = re.split("###FILE:([^#]+)###",batch)[1:]	# split batch; remove first element (before the first split)
		#print (snippets)
		while len(snippets):
			fullfilepath = os.path.join(intermediate_mdtxtDIRabs,snippets[0]+PATHS.splitmarkdownSUFFIX+'.'+PATHS.markdownEXT)
			print ("    ",fullfilepath)
			file = codecs.open(fullfilepath, mode="w", encoding="utf-8")
			file.write(snippets[1].strip())
			snippets = snippets[2:]
			file.close()

for filename in os.listdir(contentDIRabs):
	if fnmatch.fnmatch(filename,"*."+PATHS.markdownEXT):
		print("MDTXT:", filename) 
		shutil.copy( 
			os.path.join(contentDIRabs,filename), 
			os.path.join(intermediate_mdtxtDIRabs,filename) )
			
################################
######### IMAGE SERIES #########
################################
if ARGS.processimages:	
	print ("Processing Images...")
	for key,imgcol in IMG.collections.items():
		print ("%20s: "%key , list(imgcol.keys()))
		imgcol.generateImageFiles(pattern=ARGS.filterimages)
			
################
### Articles ###
################	
articleLocalRootHRef = "../.."
	
articles = ArticlesCollection(
	inputDIR=intermediate_mdtxtDIRabs, 
	pattern='*.'+PATHS.markdownEXT,
	debugoutoputDIR=os.path.join(PATHS.rootDIR,PATHS.debugHTML),
	)

# for each field in `one_element_fields` transform lists with only one element `[e]` into stand-alone elements `e`
one_element_fields = ['title','subtitle','comment','author','date','entrydate','thumbnail','link']+CONTSTRUCT.one_element_fields
articles.tryReformatFields(,(lambda x:x[0]))
articles.tryReformatFields(['thumbnail'],(lambda x:os.path.splitext(x)[0]+'_thumb'+os.path.splitext(x)[1]))

articles.detectDates()

for articleKey in articles.keys():
	articles[articleKey]['vitadate'] = TEM.VitaDate.substitute(articles[articleKey])

def firstThree(i):
	if i > 3:	return "notfirstthree"
	else:		return ""

for articleKey, articleDict in articles.items():
	previews4entryHTML = ""	
	print ( "PROCESSING:", articleKey, articleDict['localFILErel'])

	### detect and replace imageseries
	m = re.search('(~~(.+?)~~)',articleDict['content']) 
	sep = ""
	while m!= None:
		imgserKey = m.group(2)
		
		if imgserKey in IMG.collections:
			previewitemsHTML = IMG.collections[imgserKey].generateSeries(
				itemTEM=TEM.Preview_ImageSelector_Element,
				seriesTEM=TEM.Preview_ImageSelector,
				itemData=articleDict,
				counterFn=firstThree)

			imageselectorHTML = IMG.collections[imgserKey].generateSeries(
				itemTEM=TEM.ImageSelector_Element,
				seriesTEM=TEM.Preview_ImageSelector,
				itemData=articleDict,
				counterFn=firstThree)

			previews4entryHTML += sep + previewitemsHTML
			sep = """<div class="imageseries-sep">&nbsp;</div>"""	
 
			IMG.collections[imgserKey].generateSlideshowHTMLfiles(TEM.ImageFullsize,
				htmlTargetDIRrel=os.path.split(articleDict['relativeHRef'])[0].replace('/','\\'),
				relativeRootHRef=articleLocalRootHRef,
				addFields={'preview':imageselectorHTML,'backlinkHref':PATHS.indexHTMLwww,'navigator':"NAV",'rubriquespecCSS':""},slideshowSelection=None)
				
			imgseriesHTML = IMG.collections[imgserKey].generateSeries(
				itemTEM=Template(TEM.ImageSeries_Thumbnail),
				seriesTEM=Template(TEM.ImageSeries4Artcl),
				itemData={'imagepath':PATHS.imagetargetDIR},
				seriesData={'preview':previewitemsHTML} )
			oldContent = articleDict['content']
		else:
			print("IGNORED image Series:",imgserKey,"in",articleKey)
			imgseriesHTML = "---"+imgserKey+"---"
			
		articleDict['content'] = oldContent[:m.start(1)] + imgseriesHTML + oldContent[m.end(1):]
		m = re.search('(~~(.+?)~~)',articleDict['content']) 
		
	previews4entryHTML = """<span class="entry-imageseries-previews">""" + previews4entryHTML + "</span>"

	### detect and replace single images
	m = re.search('((~(.+?)~)(\[(.+?)\])?)',articleDict['content']) 
	while m!= None:
		#print (m.group(3),m.group(5))
		imgKey,imgExt = os.path.splitext(m.group(3))

		if m.group(5) == None:	imagecaption = ""
		else: imagecaption = m.group(5)
				
		singleimageHTML = """<figure><a href="%s">
	<img class="med-max" src="%s/%s/%s_medium%s" /></a>
	<figcaption>%s</figcaption></figure>""" % ( imgKey+'.'+PATHS.htmlEXT, articleLocalRootHRef,
		PATHS.imagetargetDIR, imgKey, imgExt, imagecaption)

		imagessourceHTML = "%s/%s/%s_full%s" % (articleLocalRootHRef,PATHS.imagetargetDIR,imgKey,imgExt)
		imageFullSizeDocumentHTML = TEM.ImageFullsize_onlyOne.substitute(
			imagesource=imagessourceHTML,
			author=CONTSTRUCT.author,
			relativeRootHRef=articleLocalRootHRef,
			backlinkHref=PATHS.indexHTMLwww,
			nextImageHref="",
			title="+")
		writeHTMLfile(os.path.join(targetDIRabs,articleDict['localDIRrel'],imgKey+'.'+PATHS.htmlEXT),imageFullSizeDocumentHTML)	
		
		oldContent = articleDict['content']
		articleDict['content'] = oldContent[:m.start(1)] + singleimageHTML + oldContent[m.end(1):]
			
		m = re.search('((~(.+?)~)(\[(.+?)\])?)',articleDict['content']) 
		
	if 'link' in articleDict: 	
		linkHTML = Template(TEM.ExternalLink).substitute(articleDict)
	else: 						linkHTML = ""
	
	if 'thumbnail' in articleDict:	
		thumbnailHTML = """<img class="mainentrythumbnail" src="../%s/%s" />""" % (PATHS.imagetargetDIR,articleDict['thumbnail'])
	else:	
		thumbnailHTML = ""
	
	articleDict['previewHTML'] = Template("""<div class="entry-preview">$thumbnail $imagepreviews $link</div>""").safe_substitute(
		articles[articleKey],
		imagepreviews=previews4entryHTML,link=linkHTML,thumbnail=thumbnailHTML)

	if articleDict['content'] != "":
		headerHTML = TEM.GenericHeader.safe_substitute(articleDict,stylefile="style.css")
		
		needlesHTML = CONTSTRUCT.rubriques.generateSeries(
			itemTEM=TEM.fixedNeedle,
			filterFn=(lambda k:k['THIS_ELEMENT_KEY'] in articleDict['rubriques']) )
			
		infoblockHTML = TEM.ArticleInfoblock.safe_substitute(articleDict)
		
		navHTML = CONTSTRUCT.rubriques.generateSeries(
				itemTEM=Template(TEM.NavigatorElement),
				seriesTEM=Template(TEM.Navigator_withSelectedItems),
				itemData={'selection':"notselected"},
				seriesData={'selecteditem':"",'indicatorneedles':needlesHTML,'backlinkHref':articleLocalRootHRef+'/'+PATHS.katalogrelHref},
				filterFn=(lambda k:k['THIS_ELEMENT_KEY'] in articleDict['rubriques']) )
			
		RubriqueTitlesHTML = CONTSTRUCT.rubriques.generateSeries(
			itemTEM = TEM.RubriqueCaption_unselected,
			seriesTEM = TEM.RubriqueCaptions,
			seriesData = {'selecteditem':""},
			filterFn = (lambda k:k['THIS_ELEMENT_KEY'] in articleDict['rubriques']) )

		footerHTML = TEM.Footer
		
		bodyHTML = TEM.ArticleBody.safe_substitute(articleDict,navigator=navHTML,pagefooter=footerHTML,rubriquecaptions=RubriqueTitlesHTML,articleinfoblock = infoblockHTML)
		documentHTML = TEM.GenericDocument.safe_substitute(header=headerHTML,body=bodyHTML)
		
		try: documentHTML = Template(documentHTML).substitute(globalVar,relativeRootHRef=articleLocalRootHRef)
		except Exception as e:
			print ("SKIP! Processing article %s caused Error: %s." % (articleKey,str(e)))
			continue
		
		writeHTMLfile(os.path.join(targetDIRabs,articleDict['localFILErel']),documentHTML)	
	else:
		print ( "   --empty:    ", articleKey)
			
#################################################
### Indexes (overview pages listing articles) ###
#################################################
indexhtmlFilename = 'index'+'.'+PATHS.htmlEXT 

### generate indicators		(the position bars for each rubrique)
### generate previews
for key, dict in articles.items():
	articles[key]['indicatorsHTML'] = CONTSTRUCT.rubriques.generateSeries(
		itemTEM=Template(TEM.Indicator4Entry),		
		filterFn=(lambda rubr:rubr['THIS_ELEMENT_KEY'] in dict['rubriques']) )
	
###	
### katalog (main index for all rubriques)
###
print ("processing Main Catalog")
selection = set(["event","vita","prozess","ikonen","leerverkauf","pub","training","auftrag"])

needlesHTML = TEM.leftMasterNeedle + CONTSTRUCT.rubriques.generateSeries(itemTEM=TEM.fixedNeedle) 

navHTML = CONTSTRUCT.rubriques.generateSeries(
	itemTEM=Template(TEM.NavigatorElement),
	seriesTEM=Template(TEM.Navigator_withSelectedItems),
	itemData={'selection':'neutral'},
	seriesData={'selecteditem':"", 'indicatorneedles':needlesHTML, 'backlinkHref':"../"+indexhtmlFilename}) 
												
entriesHTML = articles.generateSeries(itemTEM=TEM.indexentry['__KATALOG__'],
				itemData={
					'entryelementsHTML':"--emptyEntryElements--",
					'imagepath':PATHS.imagetargetDIR
					})

documentdict = {
	'title':CONTSTRUCT.maincataloguetitle,
	'THIS_ELEMENT_KEY':"katalog",
	'subtitle':"",
	'date':"",
	'content':entriesHTML,
	'author':CONTSTRUCT.author,
	'relativeHRef':('katalog/'+PATHS.indexHTMLwww),
	}

headerHTML = TEM.GenericHeader.safe_substitute(documentdict,stylefile="style.css")

RubriqueTitlesHTML = CONTSTRUCT.rubriques.generateSeries(
	itemTEM=TEM.RubriqueCaption_unselected,
	seriesTEM=TEM.RubriqueCaptions,
	seriesData={'selecteditem':""} )
	
RubriqueHeaderHTML = TEM.RubriqueHeader.safe_substitute(rubriqueNom="Gesamtkatalog",rubriquecomment="""<span lang="en">Facing complexity.</span>""")
	
bodyHTML = Template(TEM.IndexBody).safe_substitute(
	documentdict,
	navigator=navHTML,
	rubriquecaptions=RubriqueTitlesHTML,
	rubriqueheader=RubriqueHeaderHTML,
	pagefooter=footerHTML,
	currentrubrique="")
		
documentHTML = TEM.GenericDocument.substitute(header=headerHTML,body=bodyHTML)
documentHTML = Template(documentHTML).safe_substitute(documentdict)
documentHTML = Template(documentHTML).substitute(globalVar,relativeRootHRef="..")
localFullFilepath = os.path.join(PATHS.rootDIR,PATHS.targetDIR,'katalog',PATHS.indexHTMLlocal)
print (PATHS.rootDIR,' ',PATHS.targetDIR,' ','katalog',' ',PATHS.indexHTMLlocal) 

writeHTMLfile(localFullFilepath,documentHTML)	

###	
### indexes  (one for each rubrique)
###
relativeRootHRef = ".."

for key,dict in CONTSTRUCT.rubriques.items():
	print ("INDEX %s:"%key)		
	
	navHTMLselected  = CONTSTRUCT.rubriques.generateSeries(
		itemTEM=Template(TEM.NavigatorElement),
		itemData={'selection':'selected'},
#		seriesData={'navclass':"compact"},
		filterFn=lambda k:(k['THIS_ELEMENT_KEY'] == key) )
			
	needlesHTML = TEM.leftMasterNeedle + CONTSTRUCT.rubriques.generateSeries ( itemTEM=TEM.fixedNeedle ) 
	navHTML = CONTSTRUCT.rubriques.generateSeries(
		itemTEM=Template(TEM.NavigatorElement),
		seriesTEM=Template(TEM.Navigator_withSelectedItems),
		itemData={'selection':'notselected'},
		seriesData={'selecteditem':navHTMLselected,'indicatorneedles':needlesHTML,'backlinkHref':relativeRootHRef+'/'+PATHS.katalogrelHref},
		filterFn=lambda k:(k['THIS_ELEMENT_KEY'] != key) )
		
	IndexTitleHTML = CONTSTRUCT.rubriques.generateSeries(
		itemTEM=TEM.RubriqueCaption_selected,
		filterFn=lambda k:(k['THIS_ELEMENT_KEY'] == key) )
	RubriqueTitlesHTML = CONTSTRUCT.rubriques.generateSeries(
		itemTEM=TEM.RubriqueCaption_unselected,
		seriesTEM=TEM.RubriqueCaptions,
		seriesData={'selecteditem':IndexTitleHTML},
		filterFn=lambda k:(k['THIS_ELEMENT_KEY'] != key) )
		
	entriesHTML = articles.generateSeries(
		itemTEM=TEM.indexentry[key],
		itemData={
			'imagepath':PATHS.imagetargetDIR,
			'currentrubrique':key},	
		#seriesData={},
		filterFn=lambda d: set([key]).intersection(set(d['rubriques'])) )
	
	documentdict = {
		'title':dict['rubriqueNom'],
		'THIS_ELEMENT_KEY':key,
		'subtitle':"--kein Subtitle für Subindex--",
		'date':'--auch kein Datum--',
		'content':entriesHTML,
		'author':CONTSTRUCT.author,
		#'rubriquespecCSS':rubriquespecCSS,
		'relativeHRef':(key+'/'+PATHS.indexHTMLwww),
		}

	headerHTML = TEM.GenericHeader.safe_substitute(documentdict,stylefile="style.css")
	
	RubriqueHeaderHTML = TEM.RubriqueHeader.safe_substitute(dict)
	
	bodyHTML = Template(TEM.IndexBody).safe_substitute(
		documentdict,
		navigator=navHTML,
		rubriquecaptions=RubriqueTitlesHTML,
		pagefooter=footerHTML,
		rubriqueheader=RubriqueHeaderHTML,
		#backlinkblock="",
		currentrubrique=key)
	documentHTML = TEM.GenericDocument.substitute(header=headerHTML,body=bodyHTML)
	documentHTML = Template(documentHTML).safe_substitute(documentdict)
	documentHTML = Template(documentHTML).substitute(globalVar,relativeRootHRef=relativeRootHRef)
	localFullFilepath = os.path.join(PATHS.rootDIR,PATHS.targetDIR,documentdict['THIS_ELEMENT_KEY'],PATHS.indexHTMLlocal)
	writeHTMLfile(localFullFilepath,documentHTML)	
	
	
###############################
######### index.html #########
###############################
StartseiteHTML = Template(TEM.startpage).substitute(CONTSTRUCT.startpage,relativeRootHRef=".")
writeHTMLfile(os.path.join(targetDIRabs,indexhtmlFilename),StartseiteHTML)	

###############################
######### direct copy #########
###############################
for file in ['logo.png']:
	shutil.copy(
		os.path.join(contentDIRabs,file), targetDIRabs )
		
srcDIR = os.path.join(contentDIRabs,PATHS.documntsDIR)
dstDIR = os.path.join(targetDIRabs,PATHS.documntsDIR)

for file in os.listdir( srcDIR ):
	if os.path.isfile( os.path.join(srcDIR,file) ):
		shutil.copy( os.path.join(srcDIR,file), os.path.join(dstDIR,file))
