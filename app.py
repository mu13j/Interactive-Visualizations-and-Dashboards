from flask import Flask, jsonify, render_template
import pandas as pd
import numpy as np

import sqlalchemy
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, Text, Float, Date
import json


#Connecting to sqlite database




app = Flask(__name__)



@app.route("/")
def index():
    return render_template('index.html')


@app.route('/names')
def names():
    namecsv=pd.read_csv('DataSets/belly_button_biodiversity_samples.csv')
    samplenames=namecsv.columns.tolist()[1:]
    return jsonify(samplenames)

@app.route('/otu')
def descriptions():
    descriptioncsv=pd.read_csv('DataSets/belly_button_biodiversity_otu_id.csv')
    otudescriptions=descriptioncsv['lowest_taxonomic_unit_found'].tolist()
    return jsonify(otudescriptions)

@app.route('/metadata/<sample>')
def metadata(sample):
    meta=pd.read_csv('DataSets/Belly_Button_Biodiversity_Metadata.csv')
    meta=meta[['AGE','BBTYPE',"ETHNICITY","GENDER","LOCATION",'SAMPLEID']]
    return jsonify(meta[meta['SAMPLEID']==float(sample)].to_dict(orient='records'))

@app.route('/wfreq/<sample>')
def wfreq(sample):
    meta=pd.read_csv('DataSets/Belly_Button_Biodiversity_Metadata.csv')
    meta=meta.set_index('SAMPLEID')
    return str(int(meta.loc[float(sample)]['WFREQ']))

@app.route('/sample/<sample>')
def sample(sample):
    engine = create_engine("sqlite:///DataSets/belly_button_biodiversity.sqlite",echo=False)
    conn = engine.connect()
    Base=automap_base()
    Base.prepare(engine, reflect=True)
    otu=Base.classes.otu
    samples=Base.classes.samples
    samples_metadata=Base.classes.samples_metadata
    session=Session(engine)
    querystring='BB_'+sample
    a=conn.execute(f"select otu_id, {querystring}  from samples order by {querystring} desc").fetchall()
    otu_ids=[]
    sample_values=[]
    for i in range(0,len(a)):
        otu_ids.append(a[i][0])
        sample_values.append(a[i][1])
    return jsonify({'otu_ids':otu_ids,'sample_values':sample_values})



if __name__ == "__main__":
    app.run(debug=True)
