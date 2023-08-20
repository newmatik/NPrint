"""Initialize Flask application."""

import os
import glob
import cups
import uuid
import json
from flask import Flask, request, Response, jsonify
from labels import batchlabel, boxlabel

app = Flask(__name__)
app.config.from_pyfile("config.py")

conn = cups.Connection ()
printers = conn.getPrinters ()
errorlist = []
errorlist.clear()


def check_api_key(args):
    if not args.get('api_key'):
        errorlist.append("'api_key' missing qurey parameter")
    if args.get('api_key') != app.config.get("API_KEY"):
        errorlist.append("'api_key' is invalid")


def check_batch_args(args):
    if not args.get('printer'):
        errorlist.append("'printer' missing qurey parameter")
    if not args.get('kitting_box'):
        errorlist.append("'kitting_box' missing qurey parameter")
    if not args.get('work_order'):
        errorlist.append("'work_order' missing qurey parameter")
    if not args.get('item_code'):
        errorlist.append("'item_code' missing qurey parameter")
    if not args.get('priority'):
        errorlist.append("'priority' missing qurey parameter")
    if not args.get('sales_order'):
        errorlist.append("'sales_order' missing qurey parameter")
    if not args.get('qty'):
        errorlist.append("'qty' missing qurey parameter")
    if not args.get('description'):
        errorlist.append("'description' missing qurey parameter")
    if not args.get('type'):
        errorlist.append("'type' missing qurey parameter")


def check_box_args(args):
    if not args.get('printer'):
        errorlist.append("'printer' missing qurey parameter")
    if not args.get('kitting_box'):
        errorlist.append("'kitting_box' missing qurey parameter")
    if not args.get('work_order'):
        errorlist.append("'work_order' missing qurey parameter")
    if not args.get('item_code'):
        errorlist.append("'item_code' missing qurey parameter")
    if not args.get('priority'):
        errorlist.append("'priority' missing qurey parameter")
    if not args.get('sales_order'):
        errorlist.append("'sales_order' missing qurey parameter")
    if not args.get('qty'):
        errorlist.append("'qty' missing qurey parameter")
    if not args.get('description'):
        errorlist.append("'description' missing qurey parameter")
    if not args.get('type'):
        errorlist.append("'type' missing qurey parameter")


@app.route("/api/print_batchlabel", methods = ['POST'])
def print_batchlabel():
    args = request.args
    check_api_key(args)
    check_batch_args(args)

    """if len(errorlist) > 0:
        resp = Response(
            response=jsonify(errorlist), status=400, mimetype="application/json")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        errorlist.clear()
        return resp"""
    
    label_id = str(uuid.uuid4())
    label_file = 'labels/'+label_id+'.zpl'

    with open(label_file, 'w') as f:
        f.write(batchlabel.format(batch=args['batch'], 
                                  item_code=args['item_code'], 
                                  description_line1=args['description_line1'], 
                                  description_line2=args['description_line2'],
                                  warehouse=args['warehouse'],
                                  warehouse_parent=args['warehouse_parent'],
                                  tower=args['tower'],
                                  msl=args['msl'],
                                  qty=args['qty'],
                                  date=args['date'],
                                  user=args['user']))

    os.system('lp -d ' + args['printer'] + ' -o raw ' + label_file)

    resp = Response(
        response=json.dumps(args), status=200, mimetype="application/json")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    errorlist.clear()
    return resp


@app.route("/api/print_boxlabel", methods = ['POST'])
def print_boxlabel():
    args = request.args
    check_api_key(args)
    check_box_args(args)

    if len(errorlist) > 0:
        resp = Response(
            response=jsonify(errorlist), status=400, mimetype="application/json")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        errorlist.clear()
        return resp

    label_id = str(uuid.uuid4())
    label_file = 'labels/'+label_id+'.zpl'

    with open(label_file, 'w') as f:
        f.write(boxlabel.format(kitting_box=args['kitting_box'], 
                                  work_order=args['work_order'], 
                                  item_code=args['item_code'], 
                                  priority=args['priority'],
                                  sales_order=args['sales_order'],
                                  qty=args['qty'],
                                  description=args['description'],
                                  type=args['type']))

    os.system('lp -d ' + args['printer'] + ' -o raw ' + label_file)

    resp = Response(
        response=json.dumps(args), status=200, mimetype="application/json")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    errorlist.clear()
    return resp


@app.route("/api/get_printers", methods = ['GET'])
def get_printers():
    args = request.args
    check_api_key(args)

    if len(errorlist) > 0:
        resp = Response(
            response=jsonify(errorlist), status=400, mimetype="application/json")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        errorlist.clear()
        return resp

    return printers


@app.route("/api/clean_labels", methods = ['POST'])
def clean_labels():
    args = request.args
    check_api_key(args)

    if len(errorlist) > 0:
        resp = Response(
            response=jsonify(errorlist), status=400, mimetype="application/json")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        errorlist.clear()
        return resp

    files = glob.glob('labels/*')
    for f in files:
        os.remove(f)
    return files


# This doesn't need authentication
@app.route("/api/ping", methods = ['GET'])
#@cross_origin(headers=['Content-Type', 'Authorization'])
def ping():
    return "pong"


# This does need authentication
@app.route("/api/auth_ping", methods = ['GET'])
#@cross_origin(headers=['Content-Type', 'Authorization'])
#@requires_auth
def auth_ping():
    args = request.args
    check_api_key(args)

    if len(errorlist) > 0:
        resp = Response(
            response=jsonify(errorlist), status=400, mimetype="application/json")
        resp.headers['Access-Control-Allow-Origin'] = '*'
        errorlist.clear()
        return resp

    return "pong"