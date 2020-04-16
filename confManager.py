import os
import yaml
from configparser import ConfigParser
from supervisorApi import supervisorStat


class configPush():
    def __init__(self):
        if os.path.exists('setting.yaml'):
            with open("setting.yaml", "r") as stream:
                data = yaml.safe_load(stream)
            self.Config = data['Config']

        self.setting = self.Config['setting']
        self.ic_train = self.Config['ic_train']
        self.ic_predict = self.Config['ic_predict']
        self.nlu_train = self.Config['nlu_train']
        self.nlu_predict = self.Config['nlu_predict']
        self.ec_predict = self.Config['ec_predict']
        self.dm_predict = self.Config['dm_predict']
        self.nlg_predict = self.Config['nlg_predict']

    def icTrainConf(self, request):
        result = self.ic_train
        result['command'] = "gunicorn -c conf/train_gunicorn_conf.py -b 0.0.0.0:" + \
            str(request['port'])+" train_server:app"
        result.update(request)
        return self.subsort(result)

    def icPredictConf(self, request):
        result = self.ic_predict
        result['environment'] = "FEAT_ID="+request['ID']
        result['command'] = "gunicorn -c conf/predict_knowledge_gunicorn_conf.py -b 0.0.0.0:" + \
            str(request['port'])+" \"predict_server:get_app('knowledge', '../core/predict/config.ini', service_id="+request['ID']+")\""
        result.update(request)
        return self.subsort(result)

    def nluTrainConf(self, request):
        result = self.nlu_train
        result['command'] = "bin/lu-server -Dconfig.file=conf/prod.conf -Dpidfile.path=/dev/null -Dhttp.port=" + \
            str(request['port'])
        if self.setting['nluxmx'] != None:
            result['command'] += " -J-Xmx"+self.setting['nluxmx']
        if self.setting['nluxms'] != None:
            result['command'] += " -J-Xms"+self.setting['nluxms']
        result.update(request)
        return self.subsort(result)

    def nluPredictConf(self, request):
        result = self.nlu_predict
        result['command'] = "bin/lu-server -Dconfig.file=conf/prod.conf -Dpidfile.path=/dev/null -Dhttp.port=" + \
            str(request['port'])
        if self.setting['nluxmx'] != None:
            result['command'] += " -J-Xmx"+self.setting['nluxmx']
        if self.setting['nluxms'] != None:
            result['command'] += " -J-Xms"+self.setting['nluxms']
        result.update(request)
        return self.subsort(result)

    def ecPredictConf(self, request):
        result = self.ec_predict
        result['command'] = "bin/spellcheck-rest -Dconfig.file=conf/prod.conf -Dpidfile.path=/dev/null -Dhttp.port=" + \
            str(request['port'])
        if self.setting['ecxmx'] != None:
            result['command'] += " -J-Xmx"+self.setting['ecxmx']
        if self.setting['ecxms'] != None:
            result['command'] += " -J-Xms"+self.setting['ecxms']
        result.update(request)
        return self.subsort(result)

    def dmPredictConf(self, request):
        result = self.dm_predict
        result['command'] = "bin/itri-citc-dm -Dconfig.file=conf/prod.conf -Dpidfile.path=/dev/null -Dhttp.port=" + \
            str(request['port'])
        if self.setting['dmxmx'] != None:
            result['command'] += " -J-Xmx"+self.setting['dmxmx']
        if self.setting['dmxms'] != None:
            result['command'] += " -J-Xms"+self.setting['dmxms']
        result.update(request)
        return self.subsort(result)

    def nlgPredictConf(self, request):
        result = self.nlg_predict
        result['command'] = "bin/itri-citc-nlg -Dconfig.file=conf/prod.conf -Dpidfile.path=/dev/null -Dhttp.port=" + \
            str(request['port'])
        if self.setting['nlgxmx'] != None:
            result['command'] += " -J-Xmx"+self.setting['nlgxmx']
        if self.setting['nlgxms'] != None:
            result['command'] += " -J-Xms"+self.setting['nlgxms']
        result.update(request)
        return self.subsort(result)

    def subsort(self, mdict):
        result = {}
        filtered = {k: v for k, v in mdict.items() if v is not None}
        mdict.clear()
        mdict.update(filtered)
        if mdict['name']:
            mdict.pop('name')
        if mdict['command'].startswith('bin'):
            mdict['command'] = "bash -c \""+mdict['command']+"\""
        command = mdict.pop('command')
        result['command'] = command
        if 'environment' in mdict:
            environment = ''
            environment = mdict.pop('environment')
            result['environment'] = environment
        result.update(mdict)
        result['port'] = str(result['port'])
        return result
