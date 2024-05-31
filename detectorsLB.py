import listsLB as lst
import pagecleanersLB as pgcl
import pywikibot

'''
CE MODULE (detectorsLB.py) CONTIENT TOUS LES DÉTECTEURS DE VANDALISMES
'''
site = pywikibot.Site("fr", "wikipedia")
#MOTS ET EXPRESSIONS

PossibleEndOrStart = [' ', ',', ';', ':', '.', '?', '!', ')', '"', '«', '»', '[', ']', '/', '{', '}', "'", '(', '*', '+', '=', '<', '>']

#DETECTION DE MOTS DANS LA PAGE BASÉE SUR LES LISTES PRINCIPALES
def WEX(RecentPage):
    global PossibleEndOrStart

    Diff = pgcl.CleanWEX(RecentPage)
    OldDiff = Diff["OldDiff"]
    NewDiff = Diff["NewDiff"]

    ListNamesEXC = lst.GetGroupList("MainWordsEXC", False)
    ListNames = lst.GetGroupList("MainWords", False)

    ResultWEX = [[], [], []]

    for ListIndex in range(len(ListNames)):

        List = ListNames[ListIndex]
        ListEXC = ListNamesEXC[ListIndex]
        WordList = lst.GetList(List)
        WordListEXC = lst.GetList(ListEXC)
        
        for Word in WordList:
            
            WordU = Word.upper() #LA PAGE POUR WEX EST AUSSI EN .upper()
            
            if NewDiff.find(WordU) != -1 and OldDiff.find(WordU) == -1:
                if NewDiff[NewDiff.find(WordU) - 1] in PossibleEndOrStart and NewDiff[NewDiff.find(WordU) + len(WordU)] in PossibleEndOrStart:
                    IS_EXC = False
                    
                    for WordEXC in WordListEXC:
                        if Word in WordEXC:
                            if NewDiff.find(WordEXC.upper()) != -1 and OldDiff.find(WordEXC.upper()) == -1:
                                IS_EXC = True

                    if IS_EXC == False:
                        ResultWEX[ListIndex].append([Word, NewDiff.find(WordU)])

    return ResultWEX

#DETECTION DES CHANGEMENTS DE DATES DE NAISSANCE ET DE MORT
def AC(RecentPage):
    pass

#ANALYSE DU PASSE RECENT DE L'UTILISATEUR
def USER(RecentPage):
    global site
    ResultUSER = []
    UserToCheck = pywikibot.User(site, RecentPage['user'])
    #POURCENTAGE EDITS REVOQUÉS (derniers 75 edit max)

    TotalContrib = 0
    TotalContribReverted = 0

    ChangesToCheck = site.recentchanges(namespaces=0, changetype="edit", total=75, user=RecentPage['user'])
    for Change in ChangesToCheck:
        if "mw-reverted" in Change["tags"]:
            TotalContribReverted += 1
        TotalContrib += 1

    ResultUSER.append(TotalContrib)
    ResultUSER.append(TotalContribReverted)

    #GROUPE DE L'UTILISATEUR
    if "sysop" in UserToCheck.groups():
        ResultUSER.append("sysop")

    elif "autopatrolled" in UserToCheck.groups():
        ResultUSER.append("patrolled")

    elif "autoconfirmed" in UserToCheck.groups():
        ResultUSER.append("confirmed")

    elif len(UserToCheck.rights()) == 0:
        ResultUSER.append("ip")
    else:
        ResultUSER.append("registered")

    return ResultUSER

