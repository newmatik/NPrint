import os
import glob
import cups
import uuid
import json
from flask_restful import Resource, reqparse
from model.security import api_key_required

def check_printer(printer_name):
    if printer_name not in cups.Connection().getPrinters():
        return {'message': f'Printer \'{printer_name}\' not found', 
                'tip': 'Call api endpoint \'printers\' for all available printers'}, 404
    return None

class UpdateApiKey(Resource):
    @api_key_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('api_key', help="api_key required", required=True)
        parser.add_argument('new_api_key', help="new_api_key required", required=True)
        args = parser.parse_args(strict=False)
        api_key = args.get('api_key')
        new_api_key = args.get('new_api_key')
        if api_key == new_api_key:
            return {'message': 'No change: api_key and new_api_key are the same'}
        elif new_api_key:
            with open('.env', 'r') as f:
                lines = f.readlines()
            with open('.env', 'w') as f:
                for line in lines:
                    if line.startswith('API_KEY=') or line.startswith('API_KEY ='):
                        f.write(f'API_KEY={new_api_key}\n')
                    else:
                        f.write(line)
            os.environ['API_KEY'] = new_api_key
            return {'message': 'API key updated successfully', 
                    'new_api_key': new_api_key}
        else:
            return {'error': 'No \'new_api_key\' provided'}
        

class IndexPage(Resource):
    def get(self):
        return {'message': 'NPrint API'}

class Ping(Resource):
    def get(self):
        return {'message': 'pong'}
    
class Printers(Resource):
    @api_key_required
    def post(self):
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

class PrintLabel(Resource):
    def post(self, template_file):
        # Create the parser
        parser = reqparse.RequestParser()

        # Read the JSON file
        try:
            with open('templates/'+template_file+'.json') as f:
                parser_args = json.load(f)['parser_args']
        except FileNotFoundError:
            return {'error': 'Can not find template_file \''+template_file+'.json\''}

        # Add the arguments to the parser
        for arg in parser_args:
            parser.add_argument(arg['arg'], help=arg['help'], required=arg['required'])
            
        # Parse the arguments
        args = parser.parse_args(strict=False)

        label_id = str(uuid.uuid4())
        label_file = 'labelfiles/'+label_id+'.zpl'

        try:
            with open('templates/'+template_file+'.zpl', 'r') as f:
                template = f.read()
        except FileNotFoundError:
            return {'error': 'Can not find template_file \''+template_file+'.zpl\''}

        with open(label_file, 'w') as f:
            f.write(template.format(**args))

        result = check_printer(args['printer'])
        if result is not None:
            return result

        os.system('lp -d ' + args['printer'] + ' -o raw ' + label_file)

        return {'message': 'Label printed',
                'args': args}, 200
