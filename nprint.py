"""Initialize Flask application."""

from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from controller.api_endpoints import (
    UpdateApiKey,
    IndexPage,
    OperatingSystem,
    Ping,
    DeleteLabelFiles,
    Printers,
    PrintLabel
)

app = Flask(__name__)
app.config.from_pyfile("config.py")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

api = Api(app, prefix='/api')
api.add_resource(UpdateApiKey, '/update/api_key')
api.add_resource(IndexPage, '/')
api.add_resource(OperatingSystem, '/os')
api.add_resource(Ping, '/ping')
api.add_resource(DeleteLabelFiles, '/delete/labelfiles')
api.add_resource(Printers, '/printers')
api.add_resource(PrintLabel, '/print/<string:template_file>', endpoint='print')

if __name__ == '__main__':
    app.run(debug=True)