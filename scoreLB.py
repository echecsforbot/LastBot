import pagecleanersLB as pgcl
import lexiqueLB as lxq

'''
CE MODULE (scoreLB.py) DETERMINE UN SCORE POUR CHAQUE RÉSULTAT DES DÉTECTEURS
IL CRÉER AUSSI LE TEXTE POUR LE LOG
'''

def Score(typeDTC, data, RecentPage):

    score = 0
    ContentDisplay = ""

    #WEX
    #FORMAT : {"WBL-INS": liste ins, "WBL-OOC": liste ooc, "WBL-POOC": liste pooc}
    #FORMAT POUR CHAQUE SOUS-LISTE : [[ins1, index ins1], [ins2, index ins2]]
    if typeDTC == "WEX":
        ContextLenStart = 30
        ContextLenEnd = 30
        ContentDisplay = ""
        contextprint = ""

        NewDiff = pgcl.GetCleanWEX()["NewDiff"]
        
        WEXListIndex = 0
        for WEXList in data:
            for Word in WEXList:
                score += ((3 - WEXListIndex) ** 2) / 5

                WordI = Word[1]
                NoContext = True

                for OneLen in range(6):
                    ContextLenStart = 30 - 5 * OneLen
                    if NoContext == True:
                        try:
                            contextprint = "<nowiki>" + NewDiff[WordI - ContextLenStart:WordI].lower() + "</nowiki>'''" + NewDiff[WordI:WordI + len(Word[0])].lower() + "'''<nowiki>" + NewDiff[WordI + len(Word[0]):WordI + len(Word[0]) + ContextLenEnd].lower() + "</nowiki>"
                            NoContext = False
                        except:
                            pass
                
                if NoContext == True:
                    contextprint = "'''" + NewDiff[WordI:WordI + len(Word[0])].lower() + "'''"

                ContentDisplay = ContentDisplay + f"\n# {lxq.GetFullName(WEXListIndex)} : « {contextprint} »"

            WEXListIndex += 1

        results = [score, ContentDisplay]

        return results
    
    #AC
    #FORMAT : [DATE TYPE, OLD AGE, NEW AGE]
    if typeDTC == "AC":
        
        score += ((((data[2] - data[1])) ** 2 ** 0.5) / 5) ** 2

        ContentDisplay = f"\n# Changement de {data[0]} : '''{data[1]}''' -> '''{data[2]}'''"
        
        results = [score, ContentDisplay]

        return results
    
    #USER
    #FORMAT : [NOMBRE EDITION MAX=75, NOMBRE D'EDITIONS REVOQUEES SUR LES MAX=75 DERNIERES EDITIONS, GROUPE DE L'UTILISATEUR]
    if typeDTC == "USER":
        ContentDisplay = f"\n# '''{data[1]}''' éditions révoquées sur les '''{data[0]}''' dernières ('''{round((data[1] / data[0]) * 100)}%''')"

        if data[0] >= 5:
            if data[1] / data[0] >= 0.2:
                score += (data[1] / data[0]) * 0.8

        if data[2] == "sysop" or data[2] == "patrolled":
            score -= 100
        elif data[2] == "confirmed":
            score += 0.1
        elif data[2] == "registered":
            score += 0.25
        else:
            score += 0.6

        results = [score, ContentDisplay]

        return results
    
    #EMOJI
    #FORMAT : BOOL
    if typeDTC == "EMOJI":
        if data == True:
            ContentDisplay = "\n# Ajout d'émoticônes"

            score += 1.5

        results = [score, ContentDisplay]

        return results
