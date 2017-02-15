# -*- coding: utf-8 -*-
import codecs
import sys
import string
import datetime
from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.styles import Font


myXMLFile="ibacs-mm.xml"
myCytoFile="ibacsDB.txt"
destExcelFile = "ibacsEntites.xlsx"

# pour ne pas multiplier les try catch à chaque fois
def getAttOrNone(someAttributes, aName):
    try :
        value=someAttributes[aName]
    except KeyError:
        value=None
    return value


# MAIN PROG
#------------- pour pouvoir mettre de l'accentué partout
reload(sys)
sys.setdefaultencoding('utf8')
soup = BeautifulSoup(codecs.open(myXMLFile,  "r", "utf-8" ), "xml" )

# génération du tableau tabulé pour le graphe de dépendance
if False :
    with codecs.open(myCytoFile,'w',encoding='utf8') as fcyto:
        fcyto.write("typeNoeud\tsource\t lien\tcible\ttypeDest\n")
    # exploitation des entrée Database
        for database in soup.model.find_all('database'):
            for adomain in database.find_all('domain' ):
                dbname = getAttOrNone(database.attrs,"name")
                # db workWith domain
                cible = adomain.text
                fcyto.write("Db\t %s\t workWith \t%s \tdomain \n" %(dbname,cible))
    # recherche et ajout de tous les domaines avec leurs dépendances éventuelles
        for domain in soup.model.find_all('domain'):
            # la balise domain est utilisée aussi au sein des database. On ne veut que les principales
            if domain.parent == soup.model :
                domainName = getAttOrNone(domain.attrs,"name")
                # créer le noeud au cas où pas de dépendance
                fcyto.write("domain \t%s \n" % domainName)
                for depend in domain.find_all('depends-on'):
                    cible = depend.text
                    fcyto.write("domain \t%s \t depends-on \t%s \tdomain \n" % (domainName, cible))


    fcyto.close
# fin génération graphe de dépendances

# génération du tableur avec les entités par domaine
if True :
    # create an excel
    wb = Workbook()
    # on balaie les domaines de premier niveau
    for domain in soup.model.find_all('domain'):
    # la balise domain est utilisée aussi au sein des database. On ne veut que les principales
        if domain.parent == soup.model :
            domainName = getAttOrNone(domain.attrs,"name")
            shortName = string.replace(domainName,"Maintenance", "Mtn")
            shortName = string.replace(shortName,"Management", "Mngt")
            shortName = string.replace(shortName,"Resources", "Rscs")
            shortName = string.replace(shortName,"Troubleshooting", "Trbl")
            shortName = string.replace(shortName,"Workshops", "Wrks")
            print shortName
            shortName=shortName[0:15]
            # on nomme l'onglet courant et on en crée un autre
            ws = wb.active
            if ws.title == 'Sheet':
                ws.title = shortName
            else :
                ws = wb.create_sheet(shortName)
            ws = wb.get_sheet_by_name(shortName)
            ligne = 1
            ws.column_dimensions['A'].width = 35
            c = ws ['A'+str(ligne)]
            c.value = "Entité"
            c.font = Font( color='FF000000', italic=True, bold=True)
            ws.column_dimensions['B'].width = 120
            c = ws ['B'+str(ligne)]
            c.value = "Description"
            c.font = Font( color='FF000000', italic=True, bold=True)

            ws.column_dimensions['C'].width = 12
            ws ['C'+str(ligne)] = "Attributs"
            ws.column_dimensions['D'].width = 12
            ws ['D'+str(ligne)] = "Interfaces"
            ws.column_dimensions['E'].width = 12
            ws ['E'+str(ligne)] = "Relations"






            for entity in  domain.find_all ('element'):
                atype = getAttOrNone(entity.attrs,"type")
                point = atype.rindex('.')
                atype = atype [point+1:]
                desc = entity.find ('description')
                langue=""
                description = "??"
                if desc != None :
                    langue = getAttOrNone(desc.attrs,"lang")
                    description = desc.text
                ligne += 1
                ws ['A'+str(ligne)] = atype
                ws ['B'+str(ligne)] = description
                # on compte les attributs pour la complexité
                # Attributs
                nbre = len (entity.find_all('property'))
                nbre += len (entity.find_all('id'))
                ws ['C'+str(ligne)] = nbre
                # Interfaces
                nbreItf = len (entity.find_all('implements'))
                ws ['D'+str(ligne)] = nbreItf
                # relation
                nbreTip= len (entity.find_all('tip'))
                ws ['E'+str(ligne)] = nbreTip



    wb.save(destExcelFile)
