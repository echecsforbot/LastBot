import pywikibot
from anyascii import anyascii
import timecalcLB as tmcc
import time
import datetime
import re

'''
CE MODULE (pagecleanersLB.py) CONTIENT TOUTES LES FONCTIONS PERMETTANT
DE METTRE UN TEXTE AU PROPRE SELON LES BESOINS
'''

site = pywikibot.Site("fr", "wikipedia")
CleanWEXText = ""
CleanDiffTableText = ""

#TABLE DE COMPARAISON
def CleanDiffTable(RecentPage):
    global site
    global CleanDiffTableText

    DiffTable = pywikibot.diff.html_comparator(site.compare(RecentPage['old_revid'], RecentPage['revid'], difftype='table'))

    CleanDiffTableText = DiffTable
    return DiffTable

def GetCleanDiffTable():
    global CleanWEXPageText

    return CleanWEXPageText

#POUR LE DETECTEUR WEX
def CleanWEX(RecentPage):
    global CleanWEXText

    DiffTable = CleanDiffTable(RecentPage)
    
    OldDiffNotPRC = DiffTable['deleted-context']
    NewDiffNotPRC = DiffTable['added-context']

    OldDiff = ""
    NewDiff = ""

    for Contexte in OldDiffNotPRC:
        OldDiff = OldDiff + " " + anyascii(Contexte).upper() + " "
    for Contexte in NewDiffNotPRC:
        NewDiff = NewDiff + " " + anyascii(Contexte).upper() + " "
        
    DiffTablePRC = {
        "OldDiff":OldDiff,
        "NewDiff":NewDiff
        }

    CleanWEXText = DiffTablePRC
    return DiffTablePRC

def GetCleanWEX():
    global CleanWEXText

    return CleanWEXText

def ReadCurrentLogs():
    #LIRE currentlogs.txt
    #FORMAT CURRENTLOGS : REVID, TIMESTAMP, USER, TITLE
    with open("currentlogs.txt") as CLF:
        LogsData = CLF.readlines()

    Data = []
    DataI = 0

    for Log in LogsData:
        Data.append([])
        Log = re.split(',', Log)
        Data[DataI].append(int(Log[0]))
        Data[DataI].append(tmcc.UNEP_IS(time.mktime(datetime.datetime.strptime(Log[1],"%Y-%m-%dT%H:%M:%SZ").timetuple())))
        Data[DataI].append(int(Log[2]))
        Data[DataI].append(int(Log[3]))
        DataI += 1

    return Data

def GetTextsFromLogsPage():
    #RECUPERER LE TEXTE DES LOGS
    pageLog = pywikibot.page.BasePage(site, "Utilisateur:LastBot/Logs")
    ActualPage = pageLog.get()
    LogsTextList = re.split("|- <!-- LOGSTART -->", ActualPage)
    del LogsTextList[0]

    return LogsTextList
