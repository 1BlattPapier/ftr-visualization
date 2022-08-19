import datetime
import json
from lib2to3.pgen2.pgen import DFAState

import pandas as pd
from flask import Flask, request, render_template, jsonify
import altair as alt
import pandas
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


from db import DB


app = Flask(__name__)
db = DB()


@app.get('/dashboard')
def get_dashboard():
    return render_template('newdash.html')




@app.get('/get_chart')
def get_new_dashboard():
    alt.data_transformers.disable_max_rows()
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
    data_df = data_df.sample(frac=1)
    if len(data_df)> 10000:
        data_df = data_df.iloc[:10000,:]
    data_df = data_df.fillna(0)

    # Use either tsne or pca here
    if args.get('algo') == "PCA":
        pca = PCA()
        pca_results = pca.fit_transform(data_df)
        print("PCA")
    else:
        tsne = TSNE()
        pca_results = tsne.fit_transform(data_df)
        print("TNSE")
    graph_data = []
    for tsne_result, db_entry in zip(pca_results, db_results):
        graph_data.append({
            'text': db_entry['text'],
            'topics': db_entry['topic'],
            'emotions': db_entry['emotion'],
            'x': str(tsne_result[0]),
            'y': str(tsne_result[1]),
        })
    graph_data = pd.DataFrame(graph_data)
    selection = alt.selection_multi(fields=["top_flatten"])
    selconlyem = alt.selection_multi(fields=["em_flatten"])
    color = alt.condition(selconlyem | selection, if_true=alt.value('green'),
                          if_false=alt.value('lightgray'))

    chart = alt.Chart().mark_point().encode(
        x='x:Q',
        y='y:Q',
        color=color,
        tooltip = ['text:N', "topics:N", "emotions:N"],
    ).properties(
    width=800,
    height=600
    ).interactive()
    bars = alt.Chart().mark_bar().encode(
        x=alt.X(type="quantitative", aggregate="count"),
        y=alt.Y("em_flatten:N", sort='-x'),
        color=color
    ).add_selection(
        selconlyem
    )
    topic_bars = alt.Chart().mark_bar().encode(
        x=alt.X(type="quantitative", aggregate="count"),
        y=alt.Y("top_flatten:N", sort='-x'),
        color=color
    ).add_selection(
        selection
    )

    bars = alt.vconcat(
        bars,
        topic_bars
    )

    chart = alt.hconcat(
        chart,
        bars,
        data=graph_data
    ).transform_flatten(

        ["emotions"],
        ["em_flatten"]

    ).transform_flatten(

        ["topics"],
        ["top_flatten"]

    )
    return chart.to_json()




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
