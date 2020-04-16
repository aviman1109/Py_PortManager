from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import argparse
import datetime
from portManager import PortManager
import yaml
import os
import logging

app = Flask(__name__)
api = Api(app)
# app.logger.name = 'app'
# logger = logging.getLogger('app')


portManagerd = PortManager()


def abort_if_any_doesnt_exist(args, alist):
    nExist = []
    for k in alist:
        if args[k] == None:
            nExist.append(k)
    if nExist != []:
        abort(404, message="{} doesn't exist".format(nExist))


parser = reqparse.RequestParser()
parser.add_argument('quantity')
parser.add_argument('name')
parser.add_argument('mode')
parser.add_argument('tenantCode')
parser.add_argument('model_path')
parser.add_argument('report_path')
parser.add_argument(
    'since', type=lambda s: datetime.datetime.strptime(s, '%Y/%m/%d'))
parser.add_argument(
    'until', type=lambda s: datetime.datetime.strptime(s, '%Y/%m/%d'))
parser.add_argument('note')


class Ready(Resource):
    def get(self):
        return "PortManager beta is ready!"


class Manage(Resource):
    def get(self):
        return portManagerd.get()


class ManagePorts(Resource):
    def get(self):
        required = ['quantity']
        args = parser.parse_args()
        print(str(args))
        abort_if_any_doesnt_exist(args, required)
        return portManagerd.getAvailablePort(args)


class ManagePortStart(Resource):
    def post(self, port_num):
        required = ['name']
        args = parser.parse_args()
        print(str(args))
        abort_if_any_doesnt_exist(args, required)
        return portManagerd.portStart(args)


class ManagePortStop(Resource):
    def post(self, port_num):
        required = ['name']
        args = parser.parse_args()
        print(str(args))
        abort_if_any_doesnt_exist(args, required)
        return portManagerd.portStop(args)


class ManagePortModel(Resource):
    def get(self, port_num):
        required = ['name', 'tenantCode']
        args = parser.parse_args()
        print(str(args))
        abort_if_any_doesnt_exist(args, required)
        return portManagerd.getModel(args)

    def delete(self, port_num):
        required = ['name']
        args = parser.parse_args()
        print(str(args))
        abort_if_any_doesnt_exist(args, required)
        return portManagerd.portStop(args)


class ManagePort(Resource):
    def get(self, port_num):
        return portManagerd.getPortStat(port_num)

    def put(self, port_num):
        required = ['name', 'since', 'until', 'mode',
                    'tenantCode']
        args = parser.parse_args()
        print(str(args))
        args['port'] = port_num
        abort_if_any_doesnt_exist(args, required)
        return portManagerd.addPort(args)

    def post(self, port_num):
        required = ['name', 'since', 'until', 'mode']
        args = parser.parse_args()
        print(str(args))
        args['port'] = port_num
        abort_if_any_doesnt_exist(args, required)
        return portManagerd.updatePort(args)

    def delete(self, port_num):
        required = ['name']
        args = parser.parse_args()
        print(str(args))
        abort_if_any_doesnt_exist(args, required)
        return portManagerd.deletePort(args)


##
# Actually setup the Api resource routing here
##
api.add_resource(Ready, '/')
# 取得狀態、剩餘port個數、port range
api.add_resource(Manage, '/manage')
# 取得可使用的port(按照需求個數給予port號)
api.add_resource(ManagePorts, '/manage/port')
api.add_resource(ManagePort, '/manage/<port_num>')
api.add_resource(ManagePortStart, '/manage/<port_num>/start')
api.add_resource(ManagePortStop, '/manage/<port_num>/stop')
api.add_resource(ManagePortModel, '/manage/<port_num>/model')
logFolder = 'console_logs'
logMode = 'INFO'
if os.path.exists('setting.yaml'):
    with open("setting.yaml", "r") as stream:
        data = yaml.safe_load(stream)
    managerPort = data['managerPort']
    if 'logFolder' in data:
        logFolder = data['logFolder']
    if 'logMode' in data:
        logMode = data['logMode']

if __name__ == '__main__':
    # app.logger.name = 'app'
    # logging.basicConfig(level=(getattr(logging, logMode)),
    #                     format='[ %(asctime)s.%(msecs)03d ] %(name)-12s %(levelname)-8s %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S',
    #                     handlers=[logging.FileHandler(logFolder+'/UiTester.log', 'w', 'utf-8')])
    # console = logging.StreamHandler()
    # console.setLevel(getattr(logging, logMode))
    # formatter = logging.Formatter(
    #     '[ %(asctime)s.%(msecs)03d ] %(name)-12s %(levelname)-8s %(message)s')
    # console.setFormatter(formatter)
    # logging.getLogger('app').addHandler(console)

    # logging.info('start!!!!!!!!!')
    app.run(debug=True, port=int(managerPort), host='0.0.0.0')


# logger = logging.getLogger('app')



#         logging.info(self.setting)