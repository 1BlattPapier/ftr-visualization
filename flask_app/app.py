import datetime
import os

import pandas as pd
from flask import Flask, request, render_template, send_from_directory
from flask_caching import Cache
import altair.vegalite.v4 as alt
from sklearn.decomposition import PCA
from sklearn.manifold import MDS, Isomap, SpectralEmbedding, TSNE
from db import DB

app = Flask(__name__)
db = DB()
cache = Cache(app, config={'CACHE_TYPE': 'RedisCache', 'CACHE_REDIS_HOST': 'redis'})


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.get("/")
@cache.cached(timeout=1000)
def getstartpage():
    scount, qcount = db.gettotalcount()
    r, b, t, rq, bq, tq = db.countcountsources()
    return render_template('mother_dashboard.html', startpage=True, totlacount=scount, totlacountq=qcount,
                           twittercount=t, blogspotcount=b, redditcount=r, twittercountq=tq, blogspotcountq=bq,
                           redditcountq=rq)


@app.get('/visualization')
@cache.cached(timeout=1000)
def get_dashboard():
    return render_template('mother_dashboard.html', dashboard=True,
                           url="/get_chart?st_year=2012&end_year=2013&algo=PCA&color_sheme=Topic&mode=s&datasource=trb",
                           reloaddata=True, year_color_control=True)


@app.get("/qaf-visualization")
@cache.cached(timeout=1000)
def get_qrt_vis():
    return render_template('mother_dashboard.html', qaf_dashboard=True,
                           url="/get_chart?st_year=2012&end_year=2013&algo=PCA&color_sheme=Topic&mode=q&datasource=trb",
                           reloaddata=True, year_color_control=True)


@app.get("/heatmap")
@cache.cached(timeout=1000)
def get_heatmap():
    return render_template('mother_dashboard.html', heatmap=True,
                           url="/heatmap_data?mode=s&datasource=trb"
                           )


@app.get("/qaf_heatmap")
@cache.cached(timeout=1000)
def get_qaf_heatmap():
    return render_template('mother_dashboard.html', qaf_heatmap=True,
                           url="/heatmap_data?mode=q&datasource=trb"
                           )


@app.get('/barchart')
@cache.cached(timeout=1000)
def barchart():
    return render_template('mother_dashboard.html', barchart=True,
                           url="/get_bar_chart?mode=s&datasource=trb"
                           )


@app.get('/qaf_barchart')
def qaf_barchart():
    return render_template('mother_dashboard.html', qaf_barchart=True,
                           url="/get_bar_chart?mode=q&datasource=trb"
                           )


def emotions_topics_to_vector(db_results):
    topics_emotions = {"Society & Culture": 0,
                       "Science & Mathematics": 1,
                       "Health": 2,
                       "Education & Reference": 3,
                       "Computers & Internet": 4,
                       "Sports": 5,
                       "Business & Finance": 6,
                       "Entertainment & Music": 7,
                       "Family & Relationships": 8,
                       "Politics & Government": 9,
                       "admiration": 10,
                       "amusement": 11,
                       "anger": 12,
                       "annoyance": 13,
                       "approval": 14,
                       "caring": 15,
                       "confusion": 16,
                       "curiosity": 17,
                       "desire": 18,
                       "disappointment": 19,
                       "disapproval": 20,
                       "disgust": 21,
                       "embarrassment": 22,
                       "excitement": 23,
                       "fear": 24,
                       "gratitude": 25,
                       "grief": 26,
                       "joy": 27,
                       "love": 28,
                       "nervousness": 29,
                       "optimism": 30,
                       "pride": 31,
                       "realization": 32,
                       "relief": 33,
                       "remorse": 34,
                       "sadness": 35,
                       "surprise": 36,
                       "neutral": 37
                       }
    data = []
    for result in db_results:
        out = [0] * 38
        for k, v in (dict(zip(result['topic'], result['topic_certainty'])) | dict(
                zip(result['emotion'], result['emotion_certainty']))).items():
            out[topics_emotions[k]] = v
        data.append(out)
    return data


@app.get('/get_bar_chart')
def get_bar_chart():
    alt.data_transformers.disable_max_rows()
    args = request.args
    db_results = db.get_all_data(ftr=args.get("mode") == "s", datasource=args.get("datasource"))
    timestamp = [x["meta"]["timestamp"].year for x in db_results]
    data_df = pd.DataFrame.from_records(db_results)
    data_df.pop("meta")
    data_df["Year"] = timestamp

    year_slider = alt.binding_range(min=2001, max=2022, step=1)
    slider_selection = alt.selection_single(bind=year_slider, fields=['Year'], name="Year")

    chart = alt.Chart(data_df).mark_bar().encode(
        y=alt.Y("top_flatten:N", sort='-x', title="Topics"),
        x=alt.X(type="quantitative", aggregate="count"),
        color=alt.Color('top_flatten:N', legend=None, scale=alt.Scale(scheme='category20'))
    ).add_selection(
        slider_selection
    ).transform_filter(
        slider_selection
    ).properties(title="Topics over years").properties(
        height=600,
        width=500
    )
    chart_emotion = alt.Chart(data_df).mark_bar().encode(
        y=alt.Y("em_flatten:N", sort='-x', title="Emotions"),
        x=alt.X(type="quantitative", aggregate="count"),
        color=alt.Color('top_flatten:N', legend=None, scale=alt.Scale(scheme='category20'))
    ).add_selection(
        slider_selection
    ).transform_filter(
        slider_selection
    ).properties(title="Emotions over years").properties(
        height=600,
        width=500
    )

    chart = alt.hconcat(
        chart,
        chart_emotion,
        data=data_df
    ).transform_flatten(

        ["emotion"],
        ["em_flatten"]

    ).transform_flatten(

        ["topic"],
        ["top_flatten"]

    ).resolve_scale(
        color='independent'
    )

    return chart.to_json()


@app.get('/get_chart')
def get_new_dashboard():
    alt.data_transformers.disable_max_rows()
    args = request.args
    db_results = db.filterStatements(
        datetime.datetime(int(args.get('st_year')), 12, 1),
        datetime.datetime(int(args.get('end_year')), 12, 1), args.get("mode") == "s", datasource=args.get("datasource")
    )

    data = []
    for result in db_results:
        topic_dict = {k: v for k, v in zip(result['topic'], result['topic_certainty'])}
        emotion_dict = {k: v for k, v in zip(result['emotion'], result['emotion_certainty'])}
        topic_dict.update(emotion_dict)
        data.append(topic_dict)

    data_df = pd.DataFrame.from_records(data)
    data_df = data_df.sample(frac=1)
    if len(data_df) > 10000:
        data_df = data_df.iloc[:10000, :]
    data_df = data_df.fillna(0)

    # Use either tsne or pca here
    if args.get('algo') == "PCA":
        pca = PCA()
        pca_results = pca.fit_transform(data_df)
        print("PCA")
    else:
        tsne = TSNE(n_jobs=10, learning_rate="auto", init="pca")
        pca_results = tsne.fit_transform(data_df)
        # pca_results = umap.UMAP(n_neighbors=15,
        #              min_dist=0.3,metric='correlation').fit_transform(data_df)
        print("TNSE")
    graph_data = []
    for tsne_result, db_entry in zip(pca_results, db_results):
        graph_data.append({
            'text': db_entry['text'],
            'topics': db_entry['topic'],
            'emotions': db_entry['emotion'],
            'source': db_entry["meta"]["source"],
            'x': str(tsne_result[0]),
            'y': str(tsne_result[1]),
        })
    graph_data = pd.DataFrame(graph_data)
    brush = alt.selection(type='interval')
    selection = alt.selection_multi(fields=["top_flatten"])
    selconlyem = alt.selection_multi(fields=["em_flatten"])

    if args.get('color_sheme') == "Topic":
        color = alt.condition(selconlyem | selection | brush,
                              if_true=alt.Color('top_flatten:N', legend=None, scale=alt.Scale(scheme='category20')),
                              if_false=alt.value('lightgray'))
        color2 = alt.condition(selconlyem | selection,
                               if_true=alt.Color('top_flatten:N', legend=None, scale=alt.Scale(scheme='category20')),
                               if_false=alt.value('lightgray'))
    else:
        color2 = alt.condition(selconlyem | selection,
                               if_true=alt.Color('em_flatten:N', legend=None, scale=alt.Scale(scheme='sinebow')),
                               if_false=alt.value('lightgray'))
        color = alt.condition(selconlyem | selection | brush,
                              if_true=alt.Color('em_flatten:N', legend=None, scale=alt.Scale(scheme='sinebow')),
                              if_false=alt.value('lightgray'))

    chart = alt.Chart().mark_circle().encode(
        x='x:Q',
        y='y:Q',
        color=color,
        tooltip=['text:N', "topics:N", "emotions:N", "source:N"],

    ).properties(
        width=800,
        height=600
    ).add_selection(brush)

    bars = alt.Chart().mark_bar().encode(
        x=alt.X(type="quantitative", aggregate="count"),
        y=alt.Y("em_flatten:N", sort='-x'),
        color=color2
    ).add_selection(
        selconlyem
    ).transform_filter(
        brush
    )
    topic_bars = alt.Chart().mark_bar().encode(
        x=alt.X(type="quantitative", aggregate="count"),
        y=alt.Y("top_flatten:N", sort='-x'),
        color=color2
    ).add_selection(
        selection
    ).transform_filter(
        brush
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


@app.get("/heatmap_data")
def get_heatmap_data():
    alt.data_transformers.disable_max_rows()
    args = request.args
    db_results = db.get_all_data(ftr=args.get("mode") == "s", datasource=args.get("datasource"))
    timestamp = [x["meta"]["timestamp"].year for x in db_results]
    data_df = pd.DataFrame.from_records(db_results)
    data_df.pop("meta")
    data_df["Year"] = timestamp
    heat_topic = alt.Chart().mark_rect().encode(
        x=alt.X('Year:N', title="Year"),
        y=alt.Y("top_flatten:N", title="Topics", sort='-x'),
        color=alt.Color(type="quantitative", aggregate="count", scale=alt.Scale(scheme='lightmulti'))
    ).properties(
        height=600,
        width=500
    )
    heat_emotions = alt.Chart().mark_rect().encode(
        x='Year:N',
        y=alt.Y("em_flatten:N", title="Emotions", sort='-x'),
        color=alt.Color(type="quantitative", aggregate="count", scale=alt.Scale(scheme='lightmulti'))
    ).properties(
        height=600,
        width=500
    )
    chart = alt.hconcat(
        heat_topic,
        heat_emotions,
        data=data_df
    ).transform_flatten(

        ["emotion"],
        ["em_flatten"]

    ).transform_flatten(

        ["topic"],
        ["top_flatten"]

    ).resolve_scale(
        color='independent'
    )

    return chart.to_json()
