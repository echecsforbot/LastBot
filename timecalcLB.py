import time
import datetime
import pywikibot
import dateutil.parser as dp

'''
CE MODULE (timecalcLB.py) PERMET DE CONVERTIR DIFFERENTS FORMATS DE
TEMPS VERS D'AUTRES FORMATS DE TEMPS ET D'EFFECTUER DES CALCULS
AVEC (ISO-8601 ET UNIX EPOCH). LE FUSEAU HORRAIRE UTILISÉ EST L'UTC.
'''

#CONVERSIONS

#UNIX EPOCH VERS ISO-8601
def UNEP_IS(UnixTime):

    UNEP_PRC = datetime.datetime.utcfromtimestamp(UnixTime)
    IS_PRC = pywikibot.time.Timestamp.fromISOformat(UNEP_PRC.isoformat(), sep='T')
        
    return IS_PRC


#ISO-8601 VERS UNIX EPOCH
def IS_UNEP(ISOTime):

    IS_PRC = dp.parse(str(ISOTime))
    UNEP_PRC = IS_PRC.timestamp()

    return UNEP_PRC


#CALCULS

#ISO-8601
def CalcIS(ISOTime, RelativeTimeToAdd):
    NewISOTime = UNEP_IS(IS_UNEP(ISOTime) + RelativeTimeToAdd)

    return NewISOTime





