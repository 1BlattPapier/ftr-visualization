import datetime
import json
from lib2to3.pgen2.pgen import DFAState
from flask import Flask, request, render_template, jsonify

import pandas
from sklearn.decomposition import PCA

from db import DB


app = Flask(__name__)
db = DB()


@app.get('/dashboard')
def get_dashboard():
    args = request.args
    st_year = int(args.get('st_year'))
    end_year = int(args.get('end_year'))

    return render_template('dashboard.html', st_year=st_year, end_year=end_year)


@app.get("/data")
def get_data():
    args = request.args

    db_results = db.filterStatements(
        datetime.datetime(int(args.get('st_year')), 12, 1),
        datetime.datetime(int(args.get('end_year')), 12, 1)
    )

    data = []
    for result in db_results:
        topic_dict = {k: v for k, v in zip(result['topic'], result['topic_certainty'])}
        emotion_dict = {k: v for k, v in zip(result['emotion'], result['emotion_certainty'])}
        topic_dict.update(emotion_dict)
        data.append(topic_dict)
    data_df = pandas.DataFrame.from_records(data)
    data_df = data_df.fillna(0)

    # Use either tsne or pca here
    pca = PCA()
    pca_results = pca.fit_transform(data_df)

    graph_data = []
    for tsne_result, db_entry in zip(pca_results, db_results):
        graph_data.append({
                'text': db_entry['text'],
                'topics': db_entry['topic'],
                'emotions': db_entry['emotion'],
                'x': str(tsne_result[0]),
                'y': str(tsne_result[1]),
            })

    return json.dumps(graph_data)
