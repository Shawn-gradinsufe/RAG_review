import json
from bson import ObjectId

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


def json_format(data):
    return json.dumps(data,ensure_ascii=False,indent=4,cls=MongoJSONEncoder)
    # return json.dumps(data,ensure_ascii=False,indent=4,default=str)
