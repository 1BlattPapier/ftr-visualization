import datetime
import json
from lib2to3.pgen2.pgen import DFAState
from flask import Flask, request, render_template, jsonify

import pandas
from sklearn.manifold import TSNE

from db import DB



app = Flask(__name__)

db = DB()

@app.get("/test")
def get_test():
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

    tsne = TSNE()
    tsne_results = tsne.fit_transform(data_df)

    graph_data = []
    for data_entry, tsne_result, db_entry in zip(data, tsne_results, db_results):
        data_entry.update(
            {
                'text': db_entry['text'],
                'x': str(tsne_result[0]),
                'y': str(tsne_result[1]),
            }
        )
        graph_data.append(data_entry)

    return json.dumps(graph_data)

@app.get('/')
def get_scatter_plot():
    return render_template('scatter_chart.html')