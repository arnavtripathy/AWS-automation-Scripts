#Small poc to demonstrate aws documentdb

import collections
from flask import Flask, jsonify, request
import pymongo

#Add an entry in /etc/hosts file with docdb endpoint pointing to 127.0.0.1

#mongo --tlsAllowInvalidHostnames --tls --tlsCAFile rds-combined-ca-bundle.pem --username root --password  $password --host $host

username='root'
password=$password
clusterendpoint='127.0.0.1'
client = pymongo.MongoClient(clusterendpoint, username=username, password=password, tls='true',tlsAllowInvalidHostnames='true', tlsCAFile='rds-combined-ca-bundle.pem',retryWrites='false') 

app = Flask(__name__)
  
@app.route('/add-one-doc', methods = ['GET', 'POST'])
def add_doc():
    if(request.method == 'POST'):
        db = request.args.get('db')
        col= request.args.get('col')
        doc = request.json
        data_base= client[db]
        collection=data_base[col]
        x= collection.insert_one(doc)
        return "Document added"
@app.route('/add-many-doc', methods = ['GET', 'POST'])
def add_many_doc():
    if(request.method == 'POST'):
        db = request.args.get('db')
        col= request.args.get('col')
        doc = request.json
        data_base= client[db]
        collection=data_base[col]
        x= collection.insert_many(doc)
        return "Document added"        
@app.route('/query-doc', methods = ['GET','POST'])
def show_doc():

    if(request.method == 'POST'):
        db = request.args.get('db')
        col= request.args.get('col')
        doc = request.json
        data_base= client[db]
        collection=data_base[col]
        x= collection.find(doc)
        l=[]
        for i in x:
            l.append(i)
        return str(l)    
@app.route('/delete-doc', methods = ['GET','POST'])
def delete_doc():
    if(request.method == 'POST'):
        db = request.args.get('db')
        col= request.args.get('col')
        doc = request.json
        data_base= client[db]
        collection=data_base[col]
        x= collection.delete_one(doc)
        return "Document deleted"        
# driver function
if __name__ == '__main__':

    app.run(debug = True)
