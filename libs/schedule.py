# Contributed by Mateusz Knop (https://github.com/Persiasty)

import requests
import json
import libs.logger
import secrets
import xml.etree.ElementTree as ET
from datetime import date, datetime
from requests_ntlm import HttpNtlmAuth

class Schedule:
    def __init__(self):
        self.logger = libs.logger.get_logger(__name__)
        self.mifareSession = requests.Session()
        self.mifareSession.auth = HttpNtlmAuth(secrets.MIFARE_API_LOGIN, secrets.MIFARE_API_PASSWORD,
            self.mifareSession)

        self.studentSession = requests.Session()
        self.studentSession.auth = HttpNtlmAuth(secrets.STUDENT_API_LOGIN, secrets.STUDENT_API_PASSWORD,
            self.studentSession)

    def requestMifare(self, mid):
        url = secrets.SCHEDULE_API_URL.format(mid)
        schedule = []
        try:
            response = self.mifareSession.get(url)
            if response.status_code == 200:
                schedule = response.json()
            else:
                self.logger.error("[MifareUID: {}] HTTP return code {} \n{}".format(mid, response.status_code, response.text))
                return []
        except requests.exceptions.RequestException as e:
            # Where is the internet connection?
            self.logger.error("[MifareUID: %d] Except on connection \n%s" % (mid, e))
            return []

        result = []

        for class_node in schedule:
            class_object = {}
            start = class_node["DataRoz"].split(" ")
            if datetime.strptime(start[0], "%Y-%m-%d").date() != date.today():
                continue

            end = class_node["DataZak"].split(" ")
            stime = start[1].split(":")
            etime = end[1].split(":")

            class_object["date"] = start[0]
            class_object["start"] = {'h': int(stime[0]), 'm': int(stime[1])}
            class_object["end"] = {'h': int(etime[0]), 'm': int(etime[1])}

            if(class_node["Nazwa"].strip()):
                class_object["title"] = class_node["Nazwa"]
            else:
                class_object["title"] = class_node["Kod"]

            class_object["room"] = class_node["NazwaSali"]

            result.append(class_object)

        if(len(result) < 1):
            self.logger.debug("[MifareUID: {}] Return empty schedule".format(mid))
        else:
            self.logger.debug("[MifareUID: {}] Probably successfully".format(mid))

        return result

    def requestStudent(self, studentId):
        fromDate = toDate = date.today().isoformat()
        url = secrets.STUDENT_API_URL.format(studentId, fromDate, toDate)

        try:
            response = self.studentSession.get(url)
            if response.status_code == 200:
                schedule = ET.fromstring(response.text)
                result = []

                prefix = "{http://schemas.datacontract.org/2004/07/WebServiceMirror"
                start_tag = "{}DataRoz".format(prefix)
                end_tag = "{}DataZak".format(prefix)
                name_tag = "{}Nazwa".format(prefix)
                code_tag = "{}Kod".format(prefix)
                classroom_tag = "{}NazwaSali".format(prefix)

                for class_node in schedule:
                    class_object = {}
                    start = class_node.find(start_tag).text.split(" ")
                    end = class_node.find(end_tag).text.split(" ")
                    stime = start[1].split(":")
                    etime = end[1].split(":")

                    class_object["date"] = start[0]
                    class_object["start"] = {'h': int(stime[0]), 'm': int(stime[1])}
                    class_object["end"] = {'h': int(etime[0]), 'm': int(etime[1])}

                    if(class_node.find(name_tag).text.strip()):
                        class_object["title"] = class_node.find(name_tag).text
                    else:
                        class_object["title"] = class_node.find(code_tag).text

                    class_object["room"] = class_node.find(classroom_tag).text

                    result.append(class_object)

                return result

            else:
                self.logger.error("[studentId: {}] HTTP return code {} \n{}".format(studentId, response.status_code, response.text))
                return []
        except requests.exceptions.RequestException as e:
            self.logger.error("[studentId: {}] Exception on connection \n{}".format(studentId, e))
            return []