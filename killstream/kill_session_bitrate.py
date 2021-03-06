"""

Kill stream if bitrate is > BITRATE_LIMIT

PlexPy > Settings > Notification Agents > Scripts > Bell icon:
        [X] Notify on playback start

PlexPy > Settings > Notification Agents > Scripts > Gear icon:
        Playback Start: kill_session_bitrate.py

"""
import requests
import platform
from uuid import getnode
import unicodedata

## EDIT THESE SETTINGS ##
PLEX_HOST = ''
PLEX_PORT = 32400
PLEX_SSL = ''  # s or ''
PLEX_TOKEN = 'xxxxxx'

BITRATE_LIMIT = 4000

ignore_lst = ('')


def fetch(path, t='GET'):
    url = 'http{}://{}:{}/'.format(PLEX_SSL, PLEX_HOST, PLEX_PORT)

    headers = {'X-Plex-Token': PLEX_TOKEN,
               'Accept': 'application/json',
               'X-Plex-Provides': 'controller',
               'X-Plex-Platform': platform.uname()[0],
               'X-Plex-Platform-Version': platform.uname()[2],
               'X-Plex-Product': 'Plexpy script',
               'X-Plex-Version': '0.9.5',
               'X-Plex-Device': platform.platform(),
               'X-Plex-Client-Identifier': str(hex(getnode()))
               }

    try:
        if t == 'GET':
            r = requests.get(url + path, headers=headers, verify=False)
        elif t == 'POST':
            r = requests.post(url + path, headers=headers, verify=False)
        elif t == 'DELETE':
            r = requests.delete(url + path, headers=headers, verify=False)

        if r and len(r.content):  # incase it dont return anything

            return r.json()
        else:
            return r.content

    except Exception as e:
        print e

def kill_stream(sessionId, message):
    headers = {'X-Plex-Token': PLEX_TOKEN}
    params = {'sessionId': sessionId,
              'reason': message}
    requests.get('http{}://{}:{}/status/sessions/terminate'.format(PLEX_SSL, PLEX_HOST, PLEX_PORT),
                     headers=headers, params=params)

response  = fetch('status/sessions')

sessions = []
for video in response['MediaContainer']['Video']:
    sess_id = video['Session']['id']
    user = video['User']['title']
    title = (video['grandparentTitle'] + ' - ' if video['type'] == 'episode' else '') + video['title']
    title = unicodedata.normalize('NFKD', title).encode('ascii','ignore')
    bitrate = video['Media']['bitrate']
    sessions.append((sess_id, user, title, bitrate))

for session in sessions:
    if session[1] not in ignore_lst and int(session[3]) > BITRATE_LIMIT:
        message = "You are not allowed to stream above 4 Mbps."
        print("Killing {}'s stream of {} for {}".format(session[1], session[2], message))
        kill_stream(session[0], message)
