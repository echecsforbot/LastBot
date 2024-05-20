import listsLB as lst
import pagecleanersLB as pgcl

'''
CE MODULE (detectorsLB.py) CONTIENT TOUS LES DÉTECTEURS DE VANDALISMES
'''

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

#DETECTION DES CHANGEMENT DE DATE DE NAISSANCE ET DE MORT
def AC(RecentPage):
    CleanWEX = pgcl.GetCleanWEX()
    OldDiffNoSpace = CleanWEX["OldDiff"].replace(" ", "")
    NewDiffNoSpace = CleanWEX["NewDiff"].replace(" ", "")

    AgeDiff = 0
    AgeOldDiff = 0
    AgeNewDiff = 0
    ResultAC = [0, 0, 0]
    ParaIDList = ["NAISSANCE", "DECES"]

    for ID in ParaIDList:
        ParaID = "|DATEDE" + ID + "="
        LenParaID = len(ParaID)
        ParaIndex = OldDiffNoSpace.find(ParaID)
        
        if ParaID in OldDiffNoSpace and ParaID in NewDiffNoSpace:
            #SI LA DATE EST UN MODELE
            
            #OLDDIFF
            if OldDiffNoSpace[ParaIndex + LenParaID] == "{":
                EndTemplateIndex = ParaIndex + LenParaID
                BugPrevent = 100
                while OldDiffNoSpace[EndTemplateIndex] != "}" and BugPrevent > 1:
                    EndTemplateIndex += 1
                    BugPrevent -= 1

                if BugPrevent > 0:
                    TemplateToCheck = OldDiffNoSpace[ParaIndex + LenParaID - 1:EndTemplateIndex + 1]
                    
                    if TemplateToCheck[0] == " ":
                        TemplateToCheck = TemplateToCheck[0:]


                    TemplateToCheck.replace("}", "")
                    TemplateToCheck.replace("{", "")
                    TemplateToCheck.replace("/", "|")
                    TemplateToCheck = TemplateToCheck.split("|")

                    ElementsToDel = ["DATE", "DE", ID]
                    for Element in ElementsToDel:
                        if Element in TemplateToCheck:
                            TemplateToCheck.remove(Element)
                            
                    #NEWDIFF
                    if len(TemplateToCheck[2]) == 4:
                        
                        AgeOldDiff = int(TemplateToCheck[2])

                        ParaIndex = NewDiffNoSpace.find(ParaID)
                        
                        if NewDiffNoSpace[ParaIndex + LenParaID] == "{":
                            EndTemplateIndex = ParaIndex + LenParaID
                            BugPrevent = 100
                            while NewDiffNoSpace[EndTemplateIndex] != "}" and BugPrevent > 1:
                                EndTemplateIndex += 1
                                BugPrevent -= 1

                            if BugPrevent > 0:
                                TemplateToCheck = NewDiffNoSpace[ParaID + LenParaID - 1:EndTemplateIndex + 1]
                    
                                if TemplateToCheck[0] == " ":
                                    TemplateToCheck = TemplateToCheck[0:]

                                TemplateToCheck.replace("}", "")
                                TemplateToCheck.replace("{", "")
                                TemplateToCheck.replace("/", "|")
                                TemplateToCheck = TemplateToCheck.split("|")

                                ElementsToDel = ["DATE", "DE", ID]
                                for Element in ElementsToDel:
                                    if Element in TemplateToCheck:
                                        TemplateToCheck.remove(Element)

                        if len(TemplateToCheck[2]) == 4:
                            AgeNewDiff = int(TemplateToCheck[2])

                            AgeDiff = [((AgeNewDiff - AgeOldDiff) ** 2) ** (1 / 2), AgeOldDiff, AgeNewDiff]
    
    ResultAC = [AgeDiff, AgeOldDiff, AgeNewDiff]

    return ResultAC
