import pywikibot
import time
import timecalcLB as tmcc
import detectorsLB as dtc
import scoreLB as scr
import pagecleanersLB as pgcl

LBversion = "0.2.04"

#MENU DE DÉMARRAGE
#print("Configuration classique : WEX, AC")

#INITIALISATION
site = pywikibot.Site("fr", "wikipedia")
pageLog = pywikibot.page.BasePage(site, "Utilisateur:LastBot/Logs")

def deletelogs():
    global site
    global pageLog

    NBRDEL = 0
    #VERIFIER SI DES DIFFS ONT ETES REVOQUEES

    TimeNow = time.time()
    OldPage = pageLog.get()
    BeforeLog = OldPage[:OldPage.find("<!-- LASTBOT START -->") + len("<!-- LASTBOT START -->")]

    NewTextPageLog = BeforeLog

    #FORMAT LOGS : [[revid1, user1, logtext1], [revid2, user2, logtext2]]
    Logs = pgcl.CleanLogs(pageLog.get())

    for Log in Logs:
        #POUR CHAQUE LOG DU TABLEAU
        StartingTime = tmcc.CalcIS(tmcc.UNEP_IS(TimeNow), - 60000) #57600s = 16 heures
        EndingTime = site.server_time()
        LogsToCheck = site.recentchanges(start=StartingTime, end=EndingTime, reverse=True, changetype="edit", 
                                bot=False, top_only=False, namespaces=0, user=Log[1])
        
        #PRENDRE TOUS LES LOGS DE L'UTILISATEUR SUR LES 16 DERNIERE HEURES
        for LogToCheck in LogsToCheck:
            if LogToCheck["revid"] == Log[0]:
                if tmcc.IS_UNEP(LogToCheck["timestamp"]) > TimeNow - 57600 and "mw-reverted" not in LogToCheck["tags"]:
                    NewTextPageLog = NewTextPageLog + "\n|-" + f"{Log[2]}"
                else:
                    NBRDEL += 1

    if "|}" not in NewTextPageLog:
        NewTextPageLog = NewTextPageLog + "\n|}"

    NewTextFile = open("NewText.txt", "w")
    NewTextFile.write(NewTextPageLog)
    NewTextFile.close()
    
    NewTextFile = open("NewText.txt", "r")
    NewText = NewTextFile.read()
    NewTextFile.close()

    pageLog.put(NewText, summary=f"S-{NBRDEL}-{LBversion}", watch=None, minor=True, botflag=None, force=True, asynchronous=False, callback=None, show_diff=False)
     

#RUN
def main():
    global site
    global pageLog

    while True:
        NegativeTime = 0
        NbrCycles = -1 #int(input("Nombre de cycles (-1 = infini) : "))
        DurCycle = 30 #int(input("Durée d'un cycle en secondes (15 conseillé) : "))
    
        while NbrCycles != 0:

            #SUPPRIMER LES LOGS > 16 HEURES OU DIFF REVOQUES
            deletelogs()

            NbrCycles -= 1
            
            #RÉCUPÉRER LES RC DEPUIS X SECONDES
            TimeNow = time.time()
            StartingTime = tmcc.CalcIS(tmcc.UNEP_IS(TimeNow), - DurCycle - NegativeTime)
            EndingTime = site.server_time()
    
            #print(f"\n{StartingTime} -> {EndingTime}\n")
    
            RCList = site.recentchanges(start=StartingTime, end=EndingTime,
                                        reverse=True, changetype="edit", 
                                        bot=False, top_only=False, excludeuser="Salebot",
                                        namespaces=0)
            
            #VÉRIFIER LES RC
            for RecentPage in RCList:

                IsBroken = False
                if "mw-reverted" in RecentPage['tags']:
                    IsBroken = True

                UserToCheck = pywikibot.User(site, RecentPage['user'])
                if "sysop" in UserToCheck.groups() or "autopatrolled" in UserToCheck.groups():
                    IsBroken = True
    
                if IsBroken == False and RecentPage['user'] != "LastBot":
                    score = 0
                    ContentDisplay = ""
                    resultsDTC = []
    
                    #print(RecentPage['title'])
    
                    #FORMAT DES RESULTATS (ELEMENT DE resultsDTC): [SCORE, TEXTE POUR LE LOG]
                    #DTC + SCR
                    #WEX
                    resultsDTC.append(scr.Score("USER", dtc.USER(RecentPage), RecentPage)) #USER

                    try:
                        resultsDTC.append(scr.Score("WEX", dtc.WEX(RecentPage), RecentPage)) #WEX
                    except:
                        with open("errors.txt", "a") as ErrorFile:
                            ErrorFile.write(f"\n{site.server_time()} - WEX failed: {RecentPage['revid']} [{str(RecentPage['timestamp'])}] [{RecentPage['title']}]")


                    #SOCRE
                    for result in resultsDTC:
                        score += result[0]

                    if score >= 1:
                        #MISE EN PAGE DU LOG
                        #DETAILS DISPLAY
    
                        ContentDisplay = f"\n# Commentaire : « {RecentPage['comment']} »"

                        for result in resultsDTC:
                            ContentDisplay = ContentDisplay + result[1]

                        #TITRE
                        ScoreDisplay = ["blue", "green", "yellow", "orange", "red", "black"]
                        Couleur = ""
                        
                        if score > 1:
                            for color in ScoreDisplay:
                                if score - 1 > ScoreDisplay.index(color):
                                    Couleur = color
                        else:
                            Couleur = "blue"

                        if int(RecentPage['newlen']) - int(RecentPage['oldlen']) > 0:
                            CouleurLenDiff = "#006400|(+"
                        elif int(RecentPage['newlen']) - int(RecentPage['oldlen']) < 0:
                            CouleurLenDiff = "#8B0000|("
                        else:
                            CouleurLenDiff = "#A2A9B1|("
                            
                        LenDiff = "'''{{" + f"Coloré|{CouleurLenDiff}{int(RecentPage['newlen']) - int(RecentPage['oldlen'])})" + "}}'''"
                        CheckBox = "{{" + f"Modèle:Checkbox|checked|color={Couleur}|tick=no" + "}}" + f"'''[{round(score, 2)}]'''"
                        Heure = str(RecentPage["timestamp"])
                        HeureDisplay = "'''" + str(Heure[11:16]) + "'''"
                        TexteDuLog = "\n|-" + f"\n| {CheckBox}" + f"\n| {LenDiff}" + f"\n| {HeureDisplay}" + "\n| {{" + "Liste déroulante\n| titre = " + f"[[{RecentPage['title']}]] ([[Spécial:Diff/{RecentPage['revid']}|diff]]) par [[Utilisateur:{RecentPage['user']}|{RecentPage['user']}]] " +  f"([[Discussion utilisateur:{RecentPage['user']}|d]] • [[Spécial:Contributions/{RecentPage['user']}|c]])" + f"\n| contenu = {ContentDisplay}" + "}}"

                        OldPage = pageLog.get()
                        BeforeLog = OldPage[:OldPage.find("<!-- LASTBOT START -->") + len("<!-- LASTBOT START -->")]
                        OldLogs = OldPage[OldPage.find("<!-- LASTBOT START -->") + len("<!-- LASTBOT START -->"):len(OldPage)]

                        #FINALISATIONS
                        NewLogFile = open("LogText.txt", "w")
                        NewLogFile.write(BeforeLog + TexteDuLog + OldLogs)
                        NewLogFile.close()
                        
                        NewLogFile = open("LogText.txt", "r")
                        NouveauLog = NewLogFile.read()
                        NewLogFile.close()

                        #CREATION DU LOGS SUR LA PAGE DES LOGS
                        LogsCountFile = open("logscount.txt", "r")
                        LogsCount = int(LogsCountFile.read())
                        LogsCountFile.close()

                        LogsCountFile = open("logscount.txt", "w")
                        LogsCountFile.write(f"{LogsCount + 1}")
                        LogsCountFile.close()
                        
                        pageLog.put(NouveauLog, summary=f"Log  V{LogsCount + 1}-{LBversion}", watch=None, minor=True, botflag=None, force=True, asynchronous=False, callback=None, show_diff=False)
                        #print(score)      
    
            #CALCULS DE LA DATE DE DEBUT ET DE FIN DU CYCLE SUIVANT
            TimeDiff = time.time() - TimeNow
            if TimeDiff <= DurCycle:
                NegativeTime = 0
                time.sleep(DurCycle - TimeDiff) #PAUSE ENTRE DEUX CYCLES
            else:
                NegativeTime = (TimeDiff ** 2) ** (1 / 2) - DurCycle
    

if __name__ == '__main__':
    #pass
    main()
