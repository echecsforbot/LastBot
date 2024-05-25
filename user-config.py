import os

family = 'wikipedia'
mylang = 'fr'
usernames['wikipedia']['fr'] = 'LastBot'
authenticate['fr.wikipedia.org'] = (os.environ.get('PWB_CONSUMER_TOKEN'), os.environ.get('PWB_CONSUMER_SECRET'), os.environ.get('PWB_ACCESS_TOKEN'), os.environ.get('PWB_ACCESS_SECRET'))

