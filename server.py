#Server for Kitchen Sync
import os
import json
import bson.json_util
import flask
from flask import Flask, request, render_template
from pymongo import MongoClient
from datetime import datetime, timedelta
import sendgrid
import urllib, urllib2

app = Flask(__name__, static_url_path='/')

@app.route('/')
def root(): 

	
port = os.getenv('VCAP_APP_PORT', '5000')
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=int(port), debug=True)