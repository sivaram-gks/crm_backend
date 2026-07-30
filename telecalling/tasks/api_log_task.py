
from huey.contrib.djhuey import task
from ..models.api_log import Api_Log
import json
from decimal import Decimal

# Decimal-ah JSON-ah mathurathuku oru chinna helper
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj) # Decimal-ah float-ah mathidum
        return super(DecimalEncoder, self).default(obj)

@task()
def api_history_log(data):
    try:
        # Request and Response payloads-ah safe-ah JSON string-ah mathiduvom
        # Appo thaan Decimal prachana varaathu
        req_payload = data.get('request_payload')
        res_payload = data.get('response_payload')

        # Oru velai payloads dictionary-ah irundha, athai safe-ah encode panrom
        if isinstance(req_payload, dict):
            req_payload = json.loads(json.dumps(req_payload, cls=DecimalEncoder))
        
        if isinstance(res_payload, dict):
            res_payload = json.loads(json.dumps(res_payload, cls=DecimalEncoder))

        Api_Log.objects.create(
            user_id=data.get('user_id'),
            api_name=data.get('api_name'),
            method=data.get('method'),
            request_payload=req_payload,
            response_payload=res_payload,
            status=data.get('status_code')
        )
    except Exception as e:
        # Task fail aana log-la pakkrathuku
        print(f"Error in api_history_log: {e}")