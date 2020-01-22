from flask import Flask, render_template, request, redirect,jsonify
import requests
import json
import pymongo
import os
import ast
from utils import *


app = Flask(__name__)

MONGO_URL = os.environ.get('MONGO_URL','mongodb://localhost:27017/')
MONGO_USERNAME = os.environ.get('MONGO_USERNAME')
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')

@app.route('/')
def homepage():
    return jsonify({"status":"Query Service Running"})

@app.route('/subject/<subjectID>',methods = ['GET'])
def subjectDataSets(subjectID):

    if RepresentsInt(subjectID):

        subjectID = int(subjectID)

    else:

        return jsonify({'error':"subjectID must be of type integer"}),400

    client = pymongo.MongoClient(MONGO_URL,
                                 username=MONGO_USERNAME,
                                 password=MONGO_PASSWORD)

    db = client.ors

    query = { "subjectID": subjectID ,"@type":"NICUPatient"}
    variables = {"_id":0,'@context':0,'identifierStatus':0}

    cur =  db.ids.find(query,variables)

    subjectMeta = {}

    if cur.count() == 0:
        return jsonify({'error':'subjectID not regestired'}),400

    for subject in cur:

        subjectMeta = subject

    query = { "subjectID": subjectID ,"@type":"Dataset"}
    variables = {"@id": 1,"_id":0,'name':1,'description':1}


    cur =  db.ids.find(query,variables)

    datasetIDs = []

    for doc in cur:

        datasetIDs.append(doc)

    subjectMeta['datasetIDs'] = datasetIDs

    return jsonify(subjectMeta),200

@app.route('/query',methods = ['GET'])
def gatherSubjects():

    birthWeight = getQueryParameter('birthWeight',request)

    gestAge = getQueryParameter('gestationalAge',request)

    outcome = getQueryParameter('outcome',request)

    outcomePMA = getQueryParameter('outcomePMA',request)

    datasetID = request.args.get('datasetID')



    if datasetID == 'True' or datasetID == 'true' or datasetID == 1:

        datasetID = True

    else:

        datasetID = False



    gender = request.args.get('gender')

    if gender is not None:

        if gender in ['Male','Female']:

            gender = {'parameter':'gender',
                        'value':gender}
        else:

            gender = None

    queryParameters = [birthWeight,gestAge,gender,outcome,outcomePMA]

    valid,error = validParameters(queryParameters)

    if not valid:

        return jsonify({'error':error}),400

    query = buildQuery(queryParameters)
    variables = {"subjectID": 1,"@id":1,"_id":0}

    client = pymongo.MongoClient(MONGO_URL,
                                 username=MONGO_USERNAME,
                                 password=MONGO_PASSWORD)

    db = client.ors
    cur =  db.ids.find(query,variables)

    subjects = []

    for doc in cur:

        subject = {}

        if 'subjectID' not in doc.keys():
            continue

        subject['@id'] = doc['@id']
        subject['subjectID'] = doc['subjectID']

        subjects.append(subject)

    if not datasetID:

        return jsonify({"subjects":subjects})

    datasets = {}

    for subject in subjects:

        subjectID = subject['subjectID']

        query = { "subjectID": subjectID ,"@type":"NICUPatient"}
        variables = {"_id":0,'@context':0,'identifierStatus':0}

        cur =  db.ids.find(query,variables)

        subjectMeta = {}

        for subject in cur:

            subjectMeta = subject

        currentSubject = subjectMeta

        query = { "subjectID": subjectID ,"@type":"Dataset"}
        variables = {"@id": 1,"_id":0,'name':1,'description':1}

        cur =  db.ids.find(query,variables)

        datasetIDs = []

        for doc in cur:

            datasetIDs.append(doc)

        currentSubject['datasetIDs'] = datasetIDs

        datasets[subject['@id']] = currentSubject.copy()

    return jsonify(datasets)



if __name__ == "__main__":
    app.run(host='0.0.0.0',debug = True)
