"""Initialize Flask application."""

import os
import glob
import cups
import uuid
from flask import Flask
from flask_restful import Resource, Api, reqparse
from model.security import api_key_required

app = Flask(__name__)
app.config.from_pyfile("config.py")

def check_printer(printer_name):
    if printer_name not in cups.Connection().getPrinters():
        return {'message': f'Printer \'{printer_name}\' not found', 
                'tip': 'Call api endpoint \'printers\' for all available printers'}, 404
    return None

class IndexPage(Resource):
    def get(self):
        return {'message': 'NPrint API'}

class Ping(Resource):
    def get(self):
        return {'message': 'pong'}
    
class Printers(Resource):
    @api_key_required
    def get(self):
        conn = cups.Connection ()
        printers = conn.getPrinters ()
        return {'printers': printers}

class DeleteLabelFiles(Resource):
    @api_key_required
    def post(self):
        files = glob.glob('labelfiles/*')
        if len(files) == 0:
            return {'message': 'No label files to delete'}
        for f in files:
            os.remove(f)
        return {'message': 'Label files deleted',
                'files': files}

class PrintBatchLabel(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('printer', type=str, help='Printer to print to') \
            .add_argument('batch', type=str, help='Batch number') \
            .add_argument('item_code', type=str, help='Item code') \
            .add_argument('description_line1', type=str, help='Description line 1') \
            .add_argument('description_line2', type=str, help='Description line 2') \
            .add_argument('warehouse', type=str, help='Warehouse') \
            .add_argument('warehouse_parent', type=str, help='Warehouse parent') \
            .add_argument('tower', type=str, help='Tower') \
            .add_argument('msl', type=str, help='MSL') \
            .add_argument('qty', type=str, help='Quantity') \
            .add_argument('date', type=str, help='Date') \
            .add_argument('user', type=str, help='User')
        args = parser.parse_args()

        label_id = str(uuid.uuid4())
        label_file = 'labelfiles/'+label_id+'.zpl'

        with open('templates/batchlabel.zpl', 'r') as f:
            template = f.read()

        with open(label_file, 'w') as f:
            f.write(template.format(batch=args['batch'], 
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

        result = check_printer(args['printer'])
        if result is not None:
            return result

        os.system('lp -d ' + args['printer'] + ' -o raw ' + label_file)

        return {'message': 'Batch label printed',
                'batch': args['batch'],
                'printer': args['printer'],
                'label_id': label_id}, 200

class PrintBoxLabel(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('printer', type=str, help='Printer to print to') \
            .add_argument('kitting_box', type=str, help='Kitting box number') \
            .add_argument('work_order', type=str, help='Work order') \
            .add_argument('item_code', type=str, help='Item code') \
            .add_argument('priority', type=str, help='Priority') \
            .add_argument('sales_order', type=str, help='Sales order') \
            .add_argument('qty', type=str, help='Quantity') \
            .add_argument('description', type=str, help='Description') \
            .add_argument('type', type=str, help='Type')
        args = parser.parse_args()

        label_id = str(uuid.uuid4())
        label_file = 'labels/'+label_id+'.zpl'

        with open('templates/boxlabel.zpl', 'r') as f:
            template = f.read()

        with open(label_file, 'w') as f:
            f.write(template.format(kitting_box=args['kitting_box'],
                                    work_order=args['work_order'], 
                                    item_code=args['item_code'],
                                    priority=args['priority'],
                                    sales_order=args['sales_order'],
                                    qty=args['qty'],
                                    description=args['description'],
                                    type=args['type']))

        result = check_printer(args['printer'])
        if result is not None:
            return result

        os.system('lp -d ' + args['printer'] + ' -o raw ' + label_file)

        return {'message': 'Box label printed',
                'kitting_box': args['kitting_box'],
                'printer': args['printer']}, 200  

api = Api(app, prefix='/api')
api.add_resource(IndexPage, '/')
api.add_resource(Ping, '/ping')
api.add_resource(DeleteLabelFiles, '/delete/labelfiles')
api.add_resource(Printers, '/printers')
api.add_resource(PrintBatchLabel, '/print/batchlabel')
api.add_resource(PrintBoxLabel, '/print/boxlabel')

if __name__ == '__main__':
    app.run(debug=True)