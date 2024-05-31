import pywikibot
from anyascii import anyascii

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

def CleanLogs(pageLog):
    OldLogs = pageLog[pageLog.find("<!-- LASTBOT START -->") + len("<!-- LASTBOT START -->"):len(pageLog)]
    Logs = OldLogs.split("|-")
    for Log in range(len(Logs) -1, -1, -1):
        if len(Logs[Log]) == 0 or "]] ([[Spécial:Diff/" not in Logs[Log] or "diff]]) par [[Utilisateur:" not in Logs[Log]:
            del Logs[Log]

    cleanlogs = []
    Templates = ["]] ([[Spécial:Diff/", "diff]]) par [[Utilisateur:"]

    for Log in Logs:
        #RETROUVER LE REVID ET USER
        cleanlog = []

        for template in Templates:
            templateI = Log.find(template) + len(template)
            digitI = templateI

            while Log[digitI] != "|":
                digitI += 1

            cleanlog.append(Log[templateI:digitI])

        cleanlog.append(Logs[Log])

        cleanlogs.append(cleanlog)

    return cleanlogs
