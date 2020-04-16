import os
from configparser import ConfigParser
from xmlrpc.client import ServerProxy


class supervisorStat():
    def __init__(self, url, config, env):
        self.server = ServerProxy(url)
        self.config = config
        self.env = env

    def getVersion(self):
        return self.server.supervisor.getAPIVersion()

    def getState(self):
        return self.server.supervisor.getState()

    # def shutdown(self):
    #     return self.server.supervisor.shutdown()

    def restart(self):
        return self.server.supervisor.restart()

    def getAllConfigInfo(self):
        return self.server.supervisor.getAllConfigInfo()

    def getAllProcessInfo(self):
        return self.server.supervisor.getAllProcessInfo()

    def getProcessInfo(self, name):
        return self.server.supervisor.getProcessInfo(name)

    def startAllProcesses(self):
        return self.server.supervisor.startAllProcesses()

    def stopAllProcesses(self):
        return self.server.supervisor.stopAllProcesses()

    def startProcess(self, name):
        return self.server.supervisor.startProcess(name)

    def stopProcess(self, name):
        return self.server.supervisor.stopProcess(name)

    def methodHelp(self):
        return self.server.system.methodSignature('system.reloadConfig')

    def reloadConfig(self,  name):
        sysReturn = set
        print(name)
        if self.config != None and self.env != None:
            print("./update.sh" + " " + self.env+" "+self.config+" && echo $?")
            sysReturn = set(
                os.popen("./update.sh" + " " + self.env+" "+self.config+" && echo $?"))
        elif self.config != None:
            print("./update.sh" + " "+self.config+" && echo $?")
            sysReturn = set(
                os.popen("./update.sh" + " "+self.config+" && echo $?"))
        else:
            print("error h")
        print(sysReturn)
        if any(name in i for i in sysReturn):
            return True
        elif any("0" in i for i in sysReturn):
            return "Not update "+name
        else:
            return False

    def tailProcessLog(self, name):
        return self.server.system.tailProcessLog(name)


if __name__ == '__main__':
    supervisor = supervisorStat()
    print(supervisor.methodHelp())
    # print(supervisor.tailProcessLog("QA41_v1_5_1_qa_predict_knowledge_49102"))
