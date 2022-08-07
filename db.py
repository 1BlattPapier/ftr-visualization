from datetime import datetime
import pymongo

class DB:
    DB_CONNECTION = '***REMOVED***'
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

    def filterStatements(self, st_date: datetime, end_date: datetime):
        query = {
            'meta.timestamp': {
                '$gte': st_date,
                '$lte': end_date
            }
        }
        cursor = self.mongo_ftr_s.find(query)
        return list(cursor)