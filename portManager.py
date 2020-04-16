# import supervisorApi
import os
import yaml
from configparser import ConfigParser
from supervisorApi import supervisorStat
from confManager import configPush
import datetime


class PortManager():
    def __init__(self):
        if os.path.exists('setting.yaml'):
            with open("setting.yaml", "r") as stream:
                data = yaml.safe_load(stream)
            self.setting = data['Setting']
        else:
            print("setting file not exist!!!")
            exit

        if all(k in self.setting for k in ("url", "file", "environment")):
            self.supervisorURL = self.setting['url']+'RPC2'
            self.supervisor = supervisorStat(
                self.supervisorURL, self.setting['file'], self.setting['environment'])
        elif all(k in self.setting for k in ("url", "file")):
            self.supervisorURL = self.setting['url']+'RPC2'
            self.supervisor = supervisorStat(
                self.supervisorURL, self.setting['file'], None)
        else:
            print("error")

        self.cfg = ConfigParser()
        self.cfg.optionxform = str
        if os.path.exists(self.setting['file']):
            self.cfg.read(self.setting['file'])
        else:
            print("no supervisor config!")

    def get(self):
        result = self.supervisor.getState()
        result['lastPorts'] = len(self.lastPorts())
        result['portRange'] = [
            self.setting['portRangeDOWN'], self.setting['portRangeUP']]
        return result

    def getAvailablePort(self, request):
        '''
        取出目前Listen的port 轉型為set
        與可用port區間相減
        再取出需要的port數量
        '''
        resultPorts = {}
        result = self.lastPorts()
        resultList = [result.pop() for i in range(int(request['quantity']))]
        resultPorts['ports'] = resultList
        return resultPorts

    def getAvailableID(self):
        result = self.lastIDs()
        resultList = result.pop()
        return resultList

    def lastPorts(self):
        sysReturn = set([int(i.strip()) for i in os.popen(
            "lsof -i -P -n | grep LISTEN | awk '{print $9}' | awk -F : '{print $NF}'ssh") if i.strip()])
        for i in self.cfg.sections():
            if self.cfg.has_option(i, "port") and self.cfg.has_option(i, "command"):
                print(int(self.cfg.get(i, "port")))
                sysReturn.add(int(self.cfg.get(i, "port")))
        return sorted(set(range(self.setting['portRangeDOWN'], self.setting['portRangeUP']+1))-sysReturn, reverse=True)

    def lastIDs(self):
        availableID = set(
            range(self.setting['idRangeDOWN'], self.setting['idRangeUP']))
        for i in self.cfg.sections():
            if self.cfg.has_option(i, "ID") and self.cfg.has_option(i, "command") and int(self.cfg.get(i, "ID")) in availableID:
                availableID.remove(int(self.cfg.get(i, "ID")))
        return availableID

    def checkPortAvailable(self, port):
        result = self.lastPorts()
        return True if port in result else False

    def checkIDAvailable(self, ID):
        result = self.lastIDs()
        return True if ID in result else False

    def checkName(self, name):
        AllProcessInfo = self.supervisor.getAllProcessInfo()
        return True if name in (i['name'] for i in AllProcessInfo) else False

    def getPortName(self, port):
        for i in self.cfg.sections():
            if self.cfg.has_option(i, "port"):
                if port == self.cfg.get(i, "port"):
                    return i

    def getPortStat(self, port):
        name = self.getPortName(port)
        status = self.supervisor.getProcessInfo(name[8:])
        status['port'] = port
        status['interval'] = [self.cfg.get(
            name, "since"), self.cfg.get(name, "until")]
        return status

    def portStart(self, request):
        if self.checkName(request['name']):
            return self.supervisor.startProcess(request['name'])
        else:
            return False

    def portStop(self, request):
        if self.checkName(request['name']):
            return self.supervisor.stopProcess(request['name'])
        else:
            return False

    def addPort(self, request):
        section_name = "program:"+request['name']
        if self.checkPortAvailable(request['port']):
            return "Unavailable port"
        if not self.checkName(request['name']):
            self.cfg.add_section(section_name)
        else:
            return "Used name"
        mode = request.pop('mode')
        if mode == "ic_predict":
            ID = str(self.getAvailableID())
            if ID:
                request['ID'] = ID
            else:
                return "No ID remain"
        if self.writeConf(section_name, mode, request):
            return self.getPortStat(request['port'])
        return False

    def updatePort(self, request):
        section_name = "program:"+request['name']
        port_name = self.getPortName(request['port'])
        if not section_name == port_name:
            self.cfg.remove_section(port_name)
        mode = request.pop('mode')
        if mode == "ic_predict":
            ID = str(self.cfg.get(port_name, "ID"))
            request['ID'] = ID
        if self.writeConf(section_name, mode, request):
            return self.getPortStat(request['port'])
        return False

    def deletePort(self, request):
        section_name = "program:"+request['name']
        if self.checkName(request['name']):
            if request['model_path'] != None:
                sysReturn = set([int(i.strip()) for i in os.popen(
                    "rm -rf "+self.setting['model']+request['model_path']+" ; echo $?")])
                if sysReturn != 0:
                    return sysReturn, "model_path error"
            if request['report_path'] != None:
                sysReturn = set([int(i.strip()) for i in os.popen(
                    "rm -rf "+self.setting['model']+request['report_path']+" ; echo $?")])
                if sysReturn != 0:
                    return sysReturn, "report_path error"
            self.cfg.remove_section(section_name)
            with open('supervisord.conf', 'w') as configfile:
                self.cfg.write(configfile)
            return self.supervisor.reloadConfig(request['name'])
        else:
            return "Name not in supervisor"

    def getModel(self, request):
        sysReturn = None
        if self.checkName(request['name']):
            sysReturn = set([str(i.strip()) for i in os.popen(
                "/bin/ls -l "+self.setting['model']+request['tenantCode']+" | awk 'NR!=1{print $9}'")])
        else:
            return "something wrong"
        if sysReturn != None:
            return sysReturn

    def deleteModel(self, request):
        sysReturn = None
        if self.checkName(request['name']):
            if request['model_path'] != None:
                sysReturn = set([int(i.strip()) for i in os.popen(
                    "rm -rf "+self.setting['model']+request['model_path']+" ; echo $?")])
                if sysReturn != 0:
                    return sysReturn, "model_path error"
            if request['report_path'] != None:
                sysReturn = set([int(i.strip()) for i in os.popen(
                    "rm -rf "+self.setting['model']+request['report_path']+" ; echo $?")])
                if sysReturn != 0:
                    return sysReturn, "report_path error"
        else:
            return "something wrong"
        if sysReturn != None:
            return sysReturn

    def writeConf(self, name, mode, conf):
        config = configPush()
        request = self.dateFix(conf)
        print(request)
        if mode == "ic_train":
            result = config.icTrainConf(request)
        elif mode == "ic_predict":
            result = config.icPredictConf(request)
        elif mode == "nlu_train":
            result = config.nluTrainConf(request)
        elif mode == "nlu_predict":
            result = config.nluPredictConf(request)
        elif mode == "ec_predict":
            result = config.ecPredictConf(request)
        elif mode == "dm_predict":
            result = config.dmPredictConf(request)
        elif mode == "nlg_predict":
            result = config.nlgPredictConf(request)
        if result:
            print("result:", result)
            self.cfg[name] = result
        else:
            return False
        with open('supervisord.conf', 'w') as configfile:
            self.cfg.write(configfile)
        return self.supervisor.reloadConfig(name)

    def dateFix(self, conf):
        conf['since'] = conf['since'].strftime("%Y/%m/%d")
        conf['until'] = conf['until'].strftime("%Y/%m/%d")
        conf.pop('quantity')
        conf.pop('note')
        return conf


if __name__ == '__main__':
    config = configPush()
