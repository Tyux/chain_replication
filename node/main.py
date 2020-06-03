#!/usr/bin/env python3
from flask import Flask, request, redirect, url_for, render_template, flash
from flask import jsonify
import time
import redis
import requests
import socket

master = 'http://172.50.0.2:5000'
# master = 'master'

app = Flask(__name__)

# is_head = False
# is_tail = False

def get_ip():
    myname = socket.getfqdn(socket.gethostname())
    myaddr = socket.gethostbyname(myname)
    return myaddr

def test_is_head(myaddr):
    r = requests.get(url=master+'/get_head')
    # params
    result = eval(r.text)
    # {'status': 'get_success', 'value': '172.17.0.3'}
    head_ip = result['value']
    if myaddr==head_ip:
        return True
    else:
        return False

def test_is_tail(myaddr):
    r = requests.get(url=master+'/get_tail')
    # params
    result = eval(r.text)
    # {'status': 'get_success', 'value': '172.17.0.3'}
    tail_ip = result['value']
    if myaddr==tail_ip:
        return True
    else:
        return False

def get_prefix(myaddr):
    pass

def get_suffix(myaddr):
    pass


@app.route('/set')
def set():
    is_head = False
    is_tail = False
    key = request.args.get('key')
    value = request.args.get('value')
    r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
    r.set(key, value)
    ip = get_ip()
    url = master + '/get_suffix?ip=' + ip
    result = eval(requests.get(url=url).content)
    if 'fail' in result['status']:
        is_tail = True
    else:
        suffix = result['value']
    url = master + '/get_prefix?ip=' + ip
    result = eval(requests.get(url=url).content)
    if 'fail' in result['status']:
        is_head = True
    else:
        prefix = result['value']
    if is_tail == False:
        url = 'http://'+suffix+':5000/set?key='+key+'&value='+value
        requests.get(url=url)
    else:
        url = 'http://'+prefix+':5000/send_ack?key='+key
        requests.get(url=url)
    ret = {"status": "set_success"}
    return jsonify(ret)

@app.route('/send_ack')
def send_ack():
    key = request.args.get('key')
    is_head = False
    is_tail = False
    ip = get_ip()
    url = master + '/get_prefix?ip=' + ip
    result = eval(requests.get(url=url).content)
    if 'fail' in result['status']:
        is_head = True
    else:
        prefix = result['value']
    if is_head == False:
        url = 'http://'+prefix+':5000/send_ack?key='+key
        requests.get(url=url)
    else:
        url = master+'/get_ack?key='+key+'&flag=ok'
        requests.get(url=url)
    ret = {"status": "send_ack_success"}
    return jsonify(ret)

@app.route('/get')
def get():
    key = request.args.get('key')
    url = master + '/get_tail'
    result = eval(requests.get(url=url).content)
    tail = result['value']
    ip = get_ip()
    if tail!=ip:
        ret = {"status": "get_fail","value":"I am not tail,tail is "+ip}
        return jsonify(ret)
    else:
        r = redis.Redis(host=tail, port=6379, decode_responses=True)
        value = r.get(key)
        if value:
            ret = {"status": "get_success", "value": value}
        else:
            ret = {"status": "get_fail","value":"No such key"}
        return jsonify(ret)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)



