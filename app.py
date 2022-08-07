import datetime
from flask import Flask, request, render_template, jsonify

import pandas
import sklearn

from db import DB



app = Flask(__name__)

db = DB()

@app.get("/test")
def get_test():
    args = request.args
    results = db.filterStatements(
        datetime.datetime(int(args.get('st_year')), 12, 1),
        datetime.datetime(int(args.get('end_year')), 12, 1)
    )

    X = []
    Y = []
    for result in results:
        topic = result['topic']
        emotion_dict = {k: v for k, v in zip(result['emotion'], result['emotion_certainty'])}
        Y.append(topic)
        X.append(emotion_dict)
    x_df = pandas.DataFrame.from_records(X)
    x_df = x_df.fillna(0)
    print(x_df.values.shape)
    print(Y)
    print(x_df.head())

    file = open('altair-data-ad5eabdff90a827509b12a9aaa59bbfe.json')
    json = jsonify(next(file))

    return json

@app.get('/')
def get_scatter_plot():
    return render_template('scatter_chart.html')