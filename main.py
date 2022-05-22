from csv import DictReader
from ast import literal_eval
import re
# pprint library is used to make the output look more pretty
from pprint import pprint
from html import escape
from base import Session, engine, Base
from schema import User
from importIGDB import import_igdb

Base.metadata.create_all(engine)
session = Session()

user_id = '625aed40c46cda3ded989a0f'


def clean(s, bPurge=True):
    s = s.strip().replace('™', '').replace('®', '').replace('"', "'")
    for rx in clean.rx:
        s = rx[0].sub(rx[1], s)
    return escape(s) if bPurge else s


clean.rx = [
    (re.compile(r'\.\.\.'), '…'),
    (re.compile(r'\s+-\s+'), ' – '),
    (re.compile(r'\u0092'), '’'),  # PU2
    (re.compile(r'\u0093'), '“'),  # STS
    (re.compile(r'\u0094'), '”'),  # CCH
    (re.compile(r'\s*\u0097\s*'), ' – '),  # CCH
]

games = []
titleReplaceList = [
    (r'\.\.\.', '…'),
]  # Cleans the title

delimeter = '\t'

user = session.query(User).filter(User.name == 'Simone').first()
pprint(user.name)

with open('./test.csv', 'r', encoding='utf-8', newline='') as csvfile:
    for row in DictReader(csvfile, delimiter='\t'):
        # Fix common problems with titles
        for i in titleReplaceList:
            row['title'] = clean(re.sub(i[0], i[1], row['title']), bPurge=False)
        plist = literal_eval(row['platformList']) if row['platformList'] else []

        pprint(row['title'])

        game = import_igdb(row, user, session)
        if game:
            pprint('import')
        else:
            pprint('nofound')


session.close()
