from bson.json_util import dumps
from datetime import datetime
from flask import Flask, request
from flask_restful import Resource, Api
from pymongo import MongoClient
from pymongo.errors import WriteError
import atexit


def on_exit_app():
    print("closing application")
    client.close()


atexit.register(on_exit_app)

client = MongoClient()
database = client.test
collection = database.hockeyEvent

app = Flask(__name__)
api = Api(app)


class findHockeyEvents(Resource):
    def get(self):
        event_type = request.args.get('type')
        event_date = request.args.get('date')
        event_limit = request.args.get('limit')
        event_skip = request.args.get('skip')

        if event_skip is None or event_skip is not int:
            event_skip = 0

        if event_limit is None or event_limit is not int:
            event_limit = 30

        if event_date is not None and event_type is not None:
            query = {"type": event_type, "date": datetime.strptime(event_date, '%m-%d-%y')}
        elif event_type != None:
            query = {"type": event_type}
        elif event_date != None:
            query = {"date": datetime.strptime(event_date, '%m-%d-%y')}
        else:
            query = {}

        events_found = collection.find(query).skip(event_skip).limit(event_limit)
        list_cursor = list(events_found)
        json_response = dumps(list_cursor)
        return json_response


class createHockeyEvent(Resource):
    def post(self):
        body = request.json
        body["date"] = datetime.strptime(body["date"], '%m-%d-%y')
        try:
            insertResult = collection.insert_one(body)
            print(insertResult.getInsertedId())
            if insertResult.getInsertedId() > 0:
                return 200
            else:
                errorResponseJson = insertResult["full error"]
        except WriteError as write_error:
            print(write_error)
            return 400
        except TypeError as type_error:
            print(type_error)
            return '{\"error\":\"400\",\"errorMessage\":\"Improper JSON Array\"}',400
        except Exception as exception_error:
            print(exception_error)
            return 500


class deleteHockeyEvent(Resource):
    def delete(self, hockey_event_id):
        try:
            deleteResult = collection.delete_one({"_id": hockey_event_id})
            if deleteResult.deleted_count == 0:
                return 404
            else:
                return 200
        except Exception as exception_error:
            print(exception_error)
            return 500

api.add_resource(findHockeyEvents, '/hockeyEvent/find')
api.add_resource(createHockeyEvent, '/hockeyEvent/create')
api.add_resource(deleteHockeyEvent, '/hockeyEvent/delete/<hockey_event_id>')

if __name__ == '__main__':
    app.run(debug=True)
