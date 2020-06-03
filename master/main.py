from flask import Flask, request, redirect, url_for, render_template, flash
import time
from flask import jsonify
import redis
# from config import *
import requests
ip_list = ['172.50.0.3','172.50.0.4','172.50.0.5','172.50.0.6']
# from config import ip_list
ack_status = 'False'
ack_key = ''
app = Flask(__name__)

import socket
myname = socket.getfqdn(socket.gethostname())
myaddr = socket.gethostbyname(myname)

def get_head(ip_list):
    return ip_list[0]

def get_tail(ip_list):
    return ip_list[-1]

def get_prefix(ip,ip_list):
    if ip==ip_list[0]:
        return None
    else:
        return ip_list[ip_list.index(ip)-1]

def get_suffix(ip,ip_list):
    if ip==ip_list[-1]:
        return None
    else:
        return ip_list[ip_list.index(ip)+1]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/set')
def set():
    key = request.args.get('key')
    value = request.args.get('value')
    head = get_head(ip_list)
    # r = redis.Redis(host=head, port=6379, decode_responses=True)
    # r.set(key, value)
    url = 'http://'+head+':5000/set?key='+key+'&value='+value
    # url = 'http://'+head+'/set'
    # params={'key':key,'value':value}
    # requests.get(url=url,params=params)
    tmp_result = eval(requests.get(url=url).content)
    print(tmp_result)
    # while 1:
    #     time.sleep(0.2)
    #     url = 'http://127.0.0.1:5000/get_ack?flag=reset'
    #     result = eval(requests.get(url=url).content)
    #     if 'fail' in result['status']:
    #         pass
    #     else:
    #         value = result['value']
    #         break
    time.sleep(0.2)
    url = 'http://127.0.0.1:5000/get_ack?flag=reset'
    result = eval(requests.get(url=url).content)
    ret = {"status": "set_fail"}
    if 'fail' in result['status']:
        ret = {"status": "set_fail"}
    else:
        value = result['value']
    ret = {"status": "set_success","value":value}
    return jsonify(ret)

# ack_status = 'False'
# key = ''
@app.route('/get_ack')
def get_ack():
    key = request.args.get('key')
    global ack_key
    if key:
        ack_key = key
    flag = request.args.get('flag')
    set_success = False
    global ack_status
    if flag=='ok':
        ack_status = 'True'
        ret = {"status": "send ack ok"}
    elif flag == 'reset':
        if ack_status == 'True':
            ret = {"status": "ack_ok","value":ack_key+' set ok'}
            ack_status = 'False'
        else:
            ret = {"status": "ack_fail"}
    return jsonify(ret)


@app.route('/get')
def get():
    key = request.args.get('key')
    tail = get_tail(ip_list)
    # r = redis.Redis(host=tail, port=6379, decode_responses=True)
    # value = r.get(key)
    url = 'http://'+tail+':5000/get?key='+key
    result = eval(requests.get(url=url).content)
    if 'success' in result['status']:
        value = result['value']
    else:
        value = False
    if value:
        ret = {"status": "get_success", "value": value}
    else:
        ret = {"status": "get_fail"}
    return jsonify(ret)



@app.route('/get_head')
def flask_get_head():
    head = get_head(ip_list)
    ret = {"status": "get_success", "value": head}
    return jsonify(ret)


@app.route('/get_tail')
def flask_get_tail():
    tail = get_tail(ip_list)
    ret = {"status": "get_success", "value": tail}
    return jsonify(ret)


@app.route('/get_prefix')
def flask_get_prefix():
    ip = request.args.get('ip')
    prefix = get_prefix(ip,ip_list)
    if prefix:
        ret = {"status": "get_success", "value": prefix}
    else:
        ret = {"status": "get_fail","value":"No such key"}
    return jsonify(ret)


@app.route('/get_suffix')
def flask_get_suffix():
    ip = request.args.get('ip')
    suffix = get_suffix(ip,ip_list)
    if suffix:
        ret = {"status": "get_success", "value": suffix}
    else:
        ret = {"status": "get_fail"}
    return jsonify(ret)


@app.route('/get_all_node')
def get_all_node():
    ret = {"status": "get_success", "value": ip_list}
    return jsonify(ret)


@app.route('/get_ip')
def get_ip():
    ret = {"status": "get_success", "value": myaddr}
    return jsonify(ret)


@app.route('/insert_node')
def insert_node():
    ip = request.args.get('ip')
    ip_list.append(ip)
    ret = {"status": "insert_success", "value": ip_list}
    return jsonify(ret)


@app.route('/scan_alive')
def scan_alive():
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for ip in ip_list:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip,6379))
            sock.close()
        except:
            ip_list.remove(ip)
    ret = {"status": "scan_success", "value": ip_list}
    return jsonify(ret)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)


