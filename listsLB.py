'''
CE MODULE (listsLB.py) PERMET DE CRÉER DES LISTES DE MOTS OU EXPRESSIONS
DEPUIS LES FICHIERS .txt DE CES MÊME LISTES

L'ORDRE DES LISTES EST LE MÊME DANS TOUS LES AUTRES SCRIPTES
EX: INS, OOC, POOC
'''


#CREATION DES LISTES
ListNames = ["WBL-INS", "WBL-OOC", "WBL-POOC", "EXC-INS", "EXC-OOC", "EXC-POOC"]
AllLists = {}

for Name in ListNames:
    WBF = open(f"./lists/{Name}.txt")
    AllLists[Name] = WBF.read().split(",")
    WBF.close()


#LISTES GROUPÉES (NOMS OU CONTENU)
def GetGroupList(GroupName, Content=False):
    global ListNames
    global AllLists
    
    Groups = {
        "All":ListNames, 
        "AllEXC":["EXC-INS", "EXC-OOC", "EXC-POOC"], 
        "MainWords":["WBL-INS", "WBL-OOC", "WBL-POOC"], 
        "MainWordsEXC":["EXC-INS", "EXC-OOC", "EXC-POOC"], 
        }

    if Content == True:
        GroupContent = []
        for List in Groups[GroupName]:
            for Word in AllLists[List]:
                GroupContent.append(Word)

        return GroupContent

    else:
        return Groups[GroupName]

    
#OBTENIR LES LISTES    
def GetList(Name):
    global AllLists

    return AllLists[Name]


        
