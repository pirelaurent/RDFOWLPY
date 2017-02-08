# -*- coding: utf-8 -*-

import openpyxl
import codecs
import sys
import datetime
import rdflib
from rdflib import Graph
from rdflib.namespace import Namespace, NamespaceManager

sourceExcelFile = ".\Ontologie000.xlsx"
point = sourceExcelFile.rindex('.')
root = sourceExcelFile [:point]
destTurtleFile = root + ".ttl"
destCytoFile = root + ".graph"

class cytoGenere:
    def __init__(self, fileCyto):
        self.fCyto = fileCyto
        fCyto.write("noeud\tlabelNoeud\ttypelien\tlien\tlabelLien\tdestination\n")

    def genGraphRow(self,name,label,typeLien,lien,labelLien,destination ):
        fCyto.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (name,label,typeLien,lien,labelLien,destination))


class anExcel:

    def __init__(self, workBook, fileTTL, fCyto):
        self.wb=workBook
        self.fOwl = fileTTL
        self.fCyto=fCyto
        self.myCyto = cytoGenere(self.fCyto)

        self.sheets=[x.upper() for x in wb.get_sheet_names()]

    def coord(self, row, col):
        # deprecated workbook.sheet.cell(row,col): use coord : gives 'A1' for (0,0) etc.
        ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        offset = divmod(col,26)
        nameCol=''
        for k in range(0,offset[0]):
            nameCol+='A'
        nameCol+=ascii_uppercase[offset[1]]
        return nameCol+str(row+1)

    def createPrefix(self):
        PREFIX = 'PREFIX'
        # uppercase to avoid pbs
        if PREFIX in self.sheets :
            sheet = wb.get_sheet_by_name(wb.get_sheet_names()[self.sheets.index(PREFIX)])
            prefix = []
            nblignesvierges = 0         # arrêt après 3 lignes vierges
            for row in range(1, 1000):
                p = sheet[self.coord(row, 0)].value
                if p is not None:
                    nblignesvierges = 0
                    u = sheet[self.coord(row, 1)].value
                    prefix=prefix+[[p, u]]
                else :
                    nblignesvierges += 1
                if nblignesvierges >3:
                    break
            generePrefix="@prefix\t%s\t<%s> .\n"
            for aprefix in prefix:
                fOwl.write(generePrefix % (aprefix[0],aprefix[1]))

    def createOntology(self) :
        ONTOLOGY='ONTOLOGY'
        if ONTOLOGY in self.sheets :
            sheet = wb.get_sheet_by_name(wb.get_sheet_names()[self.sheets.index(ONTOLOGY)])
            name = sheet['A2'].value
            title = sheet['B2'].value
            description = sheet['C2'].value
            contributor = sheet['D2'].value
            genOnto =  '\n%s\t rdf:type\towl:Ontology ;\n'
            genOnto += ' \t dc:title \t"%s";\n'
            genOnto += ' \t dc:description \t"%s";\n'
            genOnto += ' \t dc:contributor \t"%s" .\n\n'
            fOwl.write(genOnto %(name, title, description, contributor))

    def createEntities(self) :
        ENTITIES = "ENTITIES"
        if ENTITIES in self.sheets :
            sheet = wb.get_sheet_by_name(wb.get_sheet_names()[self.sheets.index(ENTITIES)])
            nblignesvierges = 0         # arrêt après 3 lignes vierges
            for row in range(1,65000) :
                entity = sheet[self.coord(row, 0)].value
                if entity is not None:
                    nblignesvierges = 0         # on arrete après 3 lignes excel vierges
                    labelforgraph = None
                    genClass = '\n%s \ta \towl:Class.\n'
                    fOwl.write(genClass % entity )
                    prefLabelfr = sheet[self.coord(row, 1)].value
                    if prefLabelfr is not None :
                        genLabelfr = '%s \tskos:prefLabel \t"%s"@fr .\n'
                        fOwl.write(genLabelfr % (entity,prefLabelfr))
                        labelforgraph = prefLabelfr
                    prefLabelen = sheet[self.coord(row, 2)].value
                    if prefLabelen is not None :
                        genLabelen = '%s \tskos:prefLabel \t"%s"@en .\n'
                        fOwl.write(genLabelen % (entity,prefLabelen))
                        if labelforgraph is None :
                            labelforgraph = prefLabelen
                    comment = sheet[self.coord(row,3)].value
                    if comment is not None :
                        genComment = '%s \trdfs:comment \t"%s" .\n'
                        fOwl.write(genComment % (entity, comment))
                    # genère le noeud graphique sans lien owl:class
                    self.myCyto.genGraphRow(entity, labelforgraph,"","","","")

                    subClassOf = sheet[self.coord(row,4)].value
                    if subClassOf is not None :
                        genSubClass = '%s \trdfs:subClassOf \t %s .\n'
                        fOwl.write(genSubClass % (entity, subClassOf))
                        self.myCyto.genGraphRow(entity, labelforgraph,"subClassOf","rdfs:subClassOf","sorte de",subClassOf)
                else :
                    nblignesvierges += 1
                if nblignesvierges >3:
                    break
                # génération de la classe

    def createObjectProperties(self) :
        OBJECTPROPERTIES='OBJECTPROPERTIES'
        if OBJECTPROPERTIES in self.sheets :
            sheet = wb.get_sheet_by_name(wb.get_sheet_names()[self.sheets.index(OBJECTPROPERTIES)])
            nblignesvierges = 0         # arrêt après 3 lignes vierges
            for row in range(1,65000) :
                property = sheet[self.coord(row, 0)].value
                if property is not None :
                    nblignesvierges = 0
                    genProperty = '\n%s \ta \towl:ObjectProperty.\n'
                    fOwl.write(genProperty % property )
                    # Labels
                    labelforgraph = None

                    prefLabelfr = sheet[self.coord(row, 1)].value
                    if prefLabelfr is not None :
                        genLabelfr = '%s \tskos:prefLabel \t"%s"@fr .\n'
                        fOwl.write(genLabelfr % (property,prefLabelfr))
                        labelforgraph = prefLabelfr

                    prefLabelen = sheet[self.coord(row, 2)].value
                    if prefLabelen is not None :
                        genLabelen = '%s \tskos:prefLabel \t"%s"@en .\n'
                        fOwl.write(genLabelen % (property,prefLabelen))
                        if labelforgraph is None :
                            labelforgraph = prefLabelen
                    if labelforgraph is None :
                        labelforgraph = property
                    # domain
                    domain = sheet[self.coord(row,3)].value
                    if domain is not None :
                        genDomain = '%s \tskos:prefLabel \t"%s"@en .\n'
                        fOwl.write(genDomain % (property, domain))

                    whatrange = sheet[self.coord(row,4)].value
                    if whatrange is not None :
                        genRange = '%s \tskos:prefLabel \t"%s"@en .\n'
                        fOwl.write(genRange % (property, whatrange))

                    comment = sheet[self.coord(row,5)].value
                    if comment is not None :
                        genComment = '%s \trdfs:comment \t"%s" .\n'
                        fOwl.write(genComment % (property, comment))

                    minProperty = sheet[self.coord(row,6)].value
                    if minProperty is not None:
                        if minProperty == 0 :
                            minProperty = None
                    maxProperty = sheet[self.coord(row,7)].value
                    if maxProperty is not None:
                        if (maxProperty == "*") or (maxProperty == 'n'):
                            maxProperty = None

                    hasRestriction = ((minProperty is not None) or (maxProperty is not None )) and (domain is not None)
                    """ex:ActionCinema a owl:Class ;
                        rdfs:subClassOf
                          [ a owl:Restriction;
                            owl:onProperty my:hasMovie ;
                            owl:minCardinality "1"^^xsd:nonNegativeInteger
                          ] ."""
                    if hasRestriction :
                        genRestric = ('\n%s \t rdfs:subClassOf\n \t[ \ta owl:Restriction ;\n \t \t owl:onProperty %s ;\n')
                        fOwl.write(genRestric %(domain, property))
                        if minProperty is not None:
                            fOwl.write(' \t \towl:minCardinality \t"%s"^^xsd:noneNegativeInteger' % minProperty)
                        # must end with a . or a ; if max is following
                        if maxProperty is not None:
                            if minProperty is not None:  # il faut conclure la précédente
                                fOwl.write(' ;\n')
                            fOwl.write(' \t \towl:maxCardinality \t"%s"^^xsd:noneNegativeInteger' % maxProperty)
                        fOwl.write(' \n')
                        fOwl.write('\t] . \n')
                    # une propriété à une seule valeur est qualifiée de FunctionalPropery
                        if maxProperty is not None :
                            if maxProperty == 1 :
                                fOwl.write( '%s\t a \towl:FunctionalProperty .\n' % property)
                    # on complète le label par la cardinalité explicite si différente de *
                        cardGraph=""
                        if minProperty is not None :
                            cardGraph = str(minProperty)
                        if maxProperty is not None :
                            if cardGraph == "":
                                cardGraph = "0"
                            cardGraph = cardGraph +":"+str(maxProperty)
                        if cardGraph != "":
                            cardGraph="("+cardGraph+")"
                        labelforgraph += cardGraph
                    self.myCyto.genGraphRow(domain,"","ObjectProperty",property,labelforgraph,whatrange)
                else :
                    nblignesvierges += 1
                if nblignesvierges >3 :
                    break




# MAIN PROG
#------------- pour pouvoir mettre de l'accentué
reload(sys)
sys.setdefaultencoding('utf8')

if True :   # pour pouvoir sauter en test
    fOwl = codecs.open(destTurtleFile,'w', encoding = 'utf8')
    fCyto = codecs.open(destCytoFile,'w', encoding = 'utf8')
    now = datetime.datetime.now()
    fOwl.write('# generation depuis Excel:'+sourceExcelFile+ ' le '+now.strftime("%Y-%m-%d %H:%M")+"\n\n")
    # open excel and get sheets name
    wb = openpyxl.load_workbook(sourceExcelFile)
    # create object excelTreatment
    excel = anExcel(wb, fOwl, fCyto)
    excel.createPrefix()
    excel.createOntology()
    excel.createEntities()
    excel.createObjectProperties()
    fOwl.close()
    fCyto.close()




if  False :  # pour des essais
    # at this time a rdf/owl file exists. Open in DB

    g=rdflib.Graph()
    g.parse(destTurtleFile, format='turtle')
    for aspace in NamespaceManager(g).namespaces():
        #print aspace
        pass

    for s,p,o in g:
        print s,p,o

    # semble long et ne ramène pas le @fr  FILTER (langMatches(lang(?job),'ES'))
    gres = g.query('SELECT * WHERE { ?p a owl:Class ; skos:prefLabel ?lab. FILTER (langMatches(lang(?lab),"FR")) }')
    for row in gres:
        print("%s is aClass label %s" % row )


""" @TODO
    générer les DatatypeProperties
        tenir un dictionnaire pour les string, integer, date,etc. du XML
        mettre comme libellé S, I, D etc.
        changer l'identifiant cible à chaque fois : S1, S2, etc. de manière à ne pas relier tout au mëme

    ajouter une colonne genreLien pour mettre des symboles différents pour :
     subClassOf
     ObjectProperty
     DatatypeProperty






"""
