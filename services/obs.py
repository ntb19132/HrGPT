import datetime
import json

from upath import UPath

s3_endpoint = "https://obs.ap-southeast-3.myhuaweicloud.com"
s3_bucket = 's3://sirius-chatgpt'
s3_prefix = 'dev/hrgpt_chat_logs'
client_kwargs = {
    "endpoint_url": s3_endpoint
}


def write_log(log, order):
    file_dir = datetime.datetime.now().strftime('%Y-%m-%d')
    session_id = log['session_id']
    path = UPath(s3_bucket, s3_prefix, client_kwargs=client_kwargs)
    file_path = path.parent / (path.name + '/' + file_dir + '/' + session_id + '/' + str(order) + '.json')
    with file_path.open('wb') as file:
        file.write(json.dumps(log).encode())

# user_log = {'session_id': 'asd', 'timestamp': 1121212, 'role': 'user', 'content': 'who r u', 'docs': ['sada', 'asdada']}
# write_log(user_log,0)
