import listsLB as lst
import pagecleanersLB as pgcl
import pywikibot
from anyascii import anyascii

'''
CE MODULE (detectorsLB.py) CONTIENT TOUS LES DÉTECTEURS DE VANDALISMES
'''
site = pywikibot.Site("fr", "wikipedia")
#MOTS ET EXPRESSIONS

PossibleEndOrStart = [' ', ',', ';', ':', '.', '?', '!', ')', '"', '«', '»', '[', ']', '/', '{', '}', "'", '(', '*', '+', '=', '<', '>']
Diff = {}
OldDiff = ""
NewDiff = ""

#DETECTION DE MOTS DANS LA PAGE BASÉE SUR LES LISTES PRINCIPALES
def WEX(RecentPage):
    global PossibleEndOrStart
    global Diff
    global OldDiff
    global NewDiff

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
    global OldDiff
    global NewDiff

    Templates = ["date de naissance", "date de décès"]
    DiffsDate = []
    for Template in Templates:
        if OldDiff.find(Template) != -1 and NewDiff.find(Template) != -1:

            OldDiffI_Start = OldDiff.find(Template)
            while OldDiff[OldDiffI_Start] != "{":
                OldDiffI_Start += 1

            OldDiffI_End = OldDiffI_Start
            while OldDiff[OldDiffI_End] != "}":
                OldDiffI_End += 1

            NewDiffI_Start = NewDiff.find(Template)
            while NewDiff[NewDiffI_Start] != "{":
                NewDiffI_Start += 1
            
            NewDiffI_End = NewDiffI_Start
            while OldDiff[NewDiffI_End] != "}":
                NewDiffI_End += 1

            StartingDate = 0
            ActualI = OldDiffI_Start
            while ActualI < OldDiffI_End:
                try:
                    if int(OldDiff[ActualI:ActualI + 4]) > 0:
                        StartingDate = int(OldDiff[ActualI:ActualI + 4])
                except:
                    pass

                ActualI += 1

            EndingDate = 0
            ActualI = NewDiffI_Start
            while ActualI < NewDiffI_End:
                try:
                    if int(NewDiff[ActualI:ActualI + 4]) > 0:
                        EndingDate = int(NewDiff[ActualI:ActualI + 4])
                except:
                    pass

                ActualI =+ 1

            DiffsDate.append([Template, StartingDate, EndingDate])

    return DiffsDate

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

def EMOJI(RecentPage): 
    global Diff
    global OldDiff
    global NewDiff

    ResultEMOJI = False

    if "Émoticône" in RecentPage['tags']:
        ResultEMOJI = True
        EXC_EMO_FILE = open(f"EXC-EMO.txt")
        emojisEXC = EXC_EMO_FILE.read().split(",")
        EXC_EMO_FILE.close()

        for emoji in emojisEXC:
            emoji = anyascii(emoji)
            if NewDiff.find(emoji) != -1:
                ResultEMOJI = False
    
    return ResultEMOJI
