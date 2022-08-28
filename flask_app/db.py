import os
from datetime import datetime
import pymongo


class DB:
    DB_CONNECTION = os.environ["MONGO_STRING"]
    mongo_client = pymongo.MongoClient(DB_CONNECTION)
    mongo_future = mongo_client['ftr']
    mongo_ftr_s = mongo_future['Future_time_references']
    mongo_ftr_q = mongo_future['Future_time_references_questions']

    def filterStatements(self, topic: str, st_date: datetime, end_date: datetime):
        query = {
            'topic': topic,
            'meta.timestamp': {
                '$gte': st_date,
                '$lte': end_date
            }
        }
        cursor = self.mongo_ftr_s.find(query)
        return list(cursor)

    def get_all_data(self, ftr=True, datasource=None):
        orlist = []
        if "t" in datasource:
            orlist.append({"meta.source": "TWITTER"})
        if "r" in datasource:
            orlist.append({"meta.source": "REDDIT"})
        if "b" in datasource:
            orlist.append({"meta.source": "BLOGSPOT"})

        if ftr:
            cursor = self.mongo_ftr_s.find({"$or": orlist}, {"emotion": 1, "topic": 1, "meta.timestamp": 1, "_id": 0})
        else:
            cursor = self.mongo_ftr_q.find({}, {"emotion": 1, "topic": 1, "meta.timestamp": 1, "_id": 0})
        return list(cursor)

    def filterStatements(self, st_date: datetime, end_date: datetime, ftr=True, datasource=None):
        match = {
            'meta.timestamp': {
                '$gte': st_date,
                '$lte': end_date
            }
        }

        query = {
            'meta.timestamp': {
                '$gte': st_date,
                '$lte': end_date
            }
        }
        orlist = []
        if "t" in datasource:
            orlist.append({"meta.source": "TWITTER"})
        if "r" in datasource:
            orlist.append({"meta.source": "REDDIT"})
        if "b" in datasource:
            orlist.append({"meta.source": "BLOGSPOT"})
        query["$or"] = orlist
        print(orlist)
        if ftr:
            cursor = self.mongo_ftr_s.find(query)
        else:
            cursor = self.mongo_ftr_q.find(query)
        return list(cursor)

    def gettotalcount(self):
        return self.mongo_ftr_s.count_documents({}), self.mongo_ftr_q.count_documents({})

    def countcountsources(self, ftr=True):
        queryt = {"meta.source":
                      "TWITTER"
                  }
        queryb = {
            "meta.source":
                "BLOGSPOT"

        }
        queryr = {"meta.source":
                      "REDDIT"
                  }

        return self.mongo_ftr_s.count_documents(queryr), self.mongo_ftr_s.count_documents(
            queryb), self.mongo_ftr_s.count_documents(queryt), self.mongo_ftr_q.count_documents(
            queryr), self.mongo_ftr_q.count_documents(queryb), self.mongo_ftr_q.count_documents(queryt)
