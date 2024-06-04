import pywikibot
import time
import timecalcLB as tmcc
import detectorsLB as dtc
import scoreLB as scr
import pagecleanersLB as pgcl

LBversion = "0.2.05"

#MENU DE DÉMARRAGE
#print("Configuration classique : WEX, AC")

#INITIALISATION
site = pywikibot.Site("fr", "wikipedia")
pageLog = pywikibot.page.BasePage(site, "Utilisateur:LastBot/Logs")

def deletelogs():
    global site
    global pageLog

    CurrentLogs = pgcl.ReadCurrentLogs()
    ShouldKeepCurrentLogs = {}
    PatrolledCount = 0
    RevertedCount = 0
    #FORMAT CURRENTLOG : [REVID, TIMESTAMP, USER, TITLE]
    for currentlog in CurrentLogs:

        IsFound = False
        #CHECK MW-REVERTED
        StartingTime = tmcc.CalcIS(currentlog[1], - 120)
        EndingTime = tmcc.CalcIS(currentlog[1], 120)
        LogsMW = site.recentchanges(start=StartingTime, end=EndingTime, reverse=True, top_only=False, namespaces=0, 
                                    changetype="edit", user=currentlog[2])

        for Log in LogsMW:
            if Log['revid'] == currentlog[0]:
                if "mw-reverted" in Log['tags']:
                    IsFound = True
                    RevertedCount += 1
                    ShouldKeepCurrentLogs[currentlog[0]] = False
        
        #CHECK PATROLLED
        if IsFound == False:
            StartingTime = tmcc.CalcIS(currentlog[1], - 120)
            EndingTime = site.server_time()
            LogPTL = site.logevents(logtype='patrol', page=currentlog[3], start=StartingTime, end=EndingTime, reverse=True)

            for Log in LogPTL:
                if Log['params']['curid'] == currentlog[0]:
                    IsFound = True
                    PatrolledCount += 1
                    ShouldKeepCurrentLogs[currentlog[0]] = False

        if IsFound == False:
            ShouldKeepCurrentLogs[currentlog[0]] = True

    #CREER LA NOUVELLE PAGE
    LogsTextList = pgcl.GetTextsFromLogsPage()
    OldPage = pageLog.get()
    NewContentPage = OldPage[:OldPage.find("<!-- LASTBOT START -->") + len("<!-- LASTBOT START -->")]
    NewContentLogsData = ""

    for currentlog in CurrentLogs:
        if ShouldKeepCurrentLogs[currentlog[0]] == True:
            #DATA FILE
            for propriete in currentlog:
                NewContentLogsData = NewContentLogsData + propriete + ","

            NewContentLogsData = NewContentLogsData[:len(NewContentLogsData) - 1]
            NewContentLogsData = NewContentLogsData + "\n"

            #PAGE
            for LogText in LogsTextList:
                if '<!-- IDSTART -->' + str(currentlog[0]) in LogText:
                    NewContentPage = NewContentPage + f"|- <!-- LOGSTART -->{LogText}"
            
    if "|}" not in NewContentPage:
        NewContentPage = NewContentPage + "\n|}"

    CLF = open("currentlogs.txt", "w")
    CLF.write(NewContentLogsData)
    CLF.close()

    NewTextFile = open("NewText.txt", "w")
    NewTextFile.write(NewContentPage)
    NewTextFile.close()
    
    NewTextFile = open("NewText.txt", "r")
    NewText = NewTextFile.read()
    NewTextFile.close()

    commentpage = "S"
    if RevertedCount >= 1:
        commentpage = f"-revert:{RevertedCount}"
    if PatrolledCount >= 1:
        commentpage = commentpage + f"-patrol:{PatrolledCount}"

    commentpage = commentpage + f"-{LBversion}"

    pageLog.put(NewText, summary=commentpage, minor=True, botflag=None, force=True, 
                asynchronous=False, callback=None, show_diff=False)
    
#RUN
def main():
    global site
    global pageLog

    BeforeLog = OldPage[:OldPage.find("<!-- LASTBOT START -->") + len("<!-- LASTBOT START -->")]

    while True:
        NegativeTime = 0
        NbrCycles = -1 #int(input("Nombre de cycles (-1 = infini) : "))
        DurCycle = 60 #int(input("Durée d'un cycle en secondes (15 conseillé) : "))
    
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
                                        namespaces=0, patrolled=False)
            
            #VÉRIFIER LES RC
            for RecentPage in RCList:

                IsBroken = False
                if "mw-reverted" in RecentPage['tags']:
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
                        TexteDuLog = "\n|- <!-- LOGSTART -->" + f"\n| {CheckBox}" + f"\n| {LenDiff}" + f"\n| {HeureDisplay}" + "\n| {{" + "Liste déroulante\n| titre = " + f"[[{RecentPage['title']}]] ([[Spécial:Diff/<!-- IDSTART -->{RecentPage['revid']}|diff]]) par [[Utilisateur:{RecentPage['user']}|{RecentPage['user']}]] " +  f"([[Discussion utilisateur:{RecentPage['user']}|d]] • [[Spécial:Contributions/{RecentPage['user']}|c]])" + f"\n| contenu = {ContentDisplay}" + "}}"

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
                        
                        pageLog.put(NouveauLog, summary=f"V{LogsCount + 1}-{LBversion}", watch=None, minor=True, botflag=None, force=True, asynchronous=False, callback=None, show_diff=False)
                        #print(score)

                        #FORMAT CURRENTLOGS : REVID, TIMESTAMP, USER, TITLE
                        CLF = open("currentlogs.txt", "a")
                        CLF.write(f"{RecentPage['revid']},{RecentPage['timestamp']},{RecentPage['user']},{RecentPage['title']}\n")
                        CLF.close()
    
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
