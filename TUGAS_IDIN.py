from flask import Flask, jsonify, render_template, request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from
import numpy as np
import pandas as pd
import re
import sqlite3

abusive_ = pd.read_csv('abusive.csv')
abusive = abusive_["ABUSIVE"].tolist()
kamusalay = pd.read_csv('new_kamusalay.csv', encoding = 'latin1', header = None)
kamusalay.columns =  ['kata alay', 'kata baku']
kamus_alay = kamusalay["kata alay"].tolist()
kamus_baku = kamusalay["kata baku"].tolist()

app = Flask(__name__)
###############################################################################################################
app.json_encoder = LazyJSONEncoder

swagger_template = dict(
    info = {
        'title': LazyString(lambda:'API Documentation for Data Processing and Modeling'),
        'version': LazyString(lambda:'1.0.0'),
        'description': LazyString(lambda:'Dokumentasi API untuk Data Processing dan Modeling')
        }, host = LazyString(lambda: request.host)
    )

swagger_config = {
        "headers":[],
        "specs":[
            {
            "endpoint":'docs',
            "route":'/docs.json'
            }
        ],
        "static_url_path":"/flasgger_static",
        "swagger_ui":True,
        "specs_route":"/docs/"
    }

swagger = Swagger(app, template=swagger_template, config=swagger_config)
###############################################################################################################

@app.route("/")  # flask routing
def home():
    
    idin = {'cara masuk kedalam flask' : 'klik /docs kedalam link url'}
    
    return idin


@swag_from("docs/get16.yml", methods=['GET'])
@app.route('/get', methods = ['GET'])
def get():
    
    conn = sqlite3.connect('db.db') # Open a database File
    query = ''' select *from tweet '''

    tweet_new = pd.read_sql_query(query, conn)

    conn.commit()
    conn.close()

    data_dict = tweet_new.to_dict('record')

    return jsonify(data_dict)


@swag_from("docs/delete16.yml", methods=['DELETE'])
@app.route('/delete', methods = ['DELETE'])
def delete():

    conn = sqlite3.connect('db.db')
    query = '''DELETE FROM tweet'''

    conn.execute(query)
    conn.commit()

    return jsonify()

@swag_from("docs/post16.yml", methods=['POST'])
@app.route('/input', methods = ['POST'])
def input():
    input_json = request.get_json(force=True)
    lama = input_json['tweet']

    text = input_json['tweet']
    text = text.lower()
    text = re.split(' ', text)

    for i in text:
        for j in abusive:
            if i == j:
                index = text.index(i)
                text[index] = '*******'
    for i in text:
        for k in kamus_alay:
            if i == k:
                index1 = kamus_alay.index(i)
                index2 = text.index(i)
                text[index2] = kamus_baku[index1]

    text = ' '.join(map(str, text))
    json_text = {
        "tweet" : lama,
        "tweet_new" : text,
    }
    
    text = pd.DataFrame([json_text])

    conn = sqlite3.connect('db.db')
    text.to_sql('tweet' , conn, if_exists = 'append', index = False)
    conn.close()

    return jsonify(json_text)

@swag_from('docs/upload16.yml', methods=['POST'])
@app.route('/upload', methods=['POST'])
def uploadDoc():
    file = request.files['file']

    try:
        data = pd.read_csv(file, encoding='iso-8859-1', error_bad_lines=False)
    except:
        data = pd.read_csv(file, encoding='utf-8', error_bad_lines=False)

    data.columns =  ['tweet','HS','Abusive','HS_Individual','HS_Group','HS_Religion',
                     'HS_Race','HS_Physical','HS_Gender','HS_Other',
                     'HS_Weak','HS_Moderat','HS_Strong']
    tweet_1 = data['tweet']
    tweet = pd.DataFrame(tweet_1)
    tweet['tweet_new'] = tweet['tweet'].str.split()

    for a in range(len(tweet['tweet_new'])):
        for i in tweet['tweet_new'][a] :
            for j in abusive:
                if i == j:
                    index = tweet['tweet_new'][a].index(i)
                    tweet['tweet_new'][a][index] = '*******'

        for i in tweet['tweet_new'][a]:
            for k in kamus_alay:
                if i == k:
                    index1 = kamus_alay.index(i)
                    index2 = tweet['tweet_new'][a].index(i)
                    tweet['tweet_new'][a][index2] = kamus_baku[index1]
    
        tweet['tweet_new'][a] = ' '.join(map(str,tweet['tweet_new'][a]))
    
    conn = sqlite3.connect('db.db')
    tweet.to_sql('tweet' , conn, if_exists = 'append', index = False)

    conn.close()
    tweet = tweet.to_dict('records')

    return jsonify(tweet)


if __name__ == '__main__':
    app.run()