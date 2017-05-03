# Contributed by Mateusz Knop (https://github.com/Persiasty)

import urllib2
import json
import logging
from datetime import date, datetime
try:
    from ntlm import HTTPNtlmAuthHandler
except ImportError:
    print('There is no python-ntlm installed')
    print('Install it by: pip install python-ntlm')
    exit()


class Schedule:
    SCHAPI_URL = "http://api.knopers.com.pl/test/data2.json?mid=%d"

    def __init__(self):
        self.logger = logging.getLogger('Mirror.Schedule')
        hdlr = logging.FileHandler('schedule.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.WARNING)
        pass

    def setCredentials(self, login, password):
        self.login = login
        self.password = password

    def requestSchedule(self, mid):
        url = Schedule.SCHAPI_URL % mid

        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url, self.login, self.password)
        # create the NTLM authentication handler
        authNTLM = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)

        # create and install the opener
        opener = urllib2.build_opener(authNTLM)
        urllib2.install_opener(opener)

        response = []
        try:
            resp = urllib2.urlopen(url)
            if resp.getcode() == 200:
                response = resp.read()
            else:
                self.logger.debug("[MifareUID: %d] HTTP return code %d \n%s" % (mid, resp.getcode(), resp.info()))
                return []
            # 400 - not found or processing error or something else went wrong
        except urllib2.URLError as e:
            # Where is the internet connection?
            self.logger.debug("[MifareUID: %d] Except on connection \n%s" % (mid, e))
            return []

        scheduleObj = []
        try:
            scheduleObj = json.loads(response)
        except:
            self.logger.debug("[MifareUID: %d] Except on Parse \n%s" % (mid, response))

        ret = []
        for event in scheduleObj:
            ev = {}
            start = event["DataRoz"].split(" ")
            if datetime.strptime(start[0], "%Y-%m-%d").date() != date.today():
                continue

            end = event["DataZak"].split(" ")
            stime = start[1].split(":")
            etime = end[1].split(":")

            ev["date"] = start[0]
            ev["start"] = {'h': int(stime[0]), 'm': int(stime[1])}
            ev["end"] = {'h': int(etime[0]), 'm': int(etime[1])}
            ev["delta"] = (ev["end"]['h'] - ev["start"]['h']) * 60 + (ev["end"]['m'] - ev["start"]['m'])
            ev["inrow"] = 1
            ev['margin'] = 0

            for e in ret:
                if (ev["start"]['h'] >= e["start"]['h']) and \
                    (ev["end"]['h'] <= e["end"]['h']) and \
                    (ev["date"] == e["date"]):
                    ev['inrow'] += 1
                    ev['margin'] += 1
                    e['inrow'] += 1

            if(event["Nazwa"].strip()):
                ev["title"] = event["Nazwa"]
            else:
                ev["title"] = event["Kod"]
            ev["room"] = event["NazwaSali"]

            ret.append(ev)

        if(len(ret) < 1):
            self.logger.debug("[MifareUID: %d] Return empty schedule" % (mid,))
        else:
            self.logger.debug("[MifareUID: %d] Probably successfully" % (mid,))

        return ret
