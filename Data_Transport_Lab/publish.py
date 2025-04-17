import json 
import time
from google.cloud import pubsub_v1
from datetime import datetime
from concurrent import futures

def future_callback(future):
    try:
        future.result()  # Wait for the result of the publish operation.
    except Exception as e:
        print(f"An error occurred: {e}")


# TODO(developer)
project_id = "pro-sylph-456318-m0"
topic_id = "my-topic"

publisher = pubsub_v1.PublisherClient()
# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_id}`
topic_path = publisher.topic_path(project_id, topic_id)

print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

with open("master.json", "r") as f:
    records = json.load(f)

print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
start_time = time.time()

count = 0
future_list = []
# create int count
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

for record in records:
    data_str = json.dumps(record, indent=4)
    # Data must be a bytestring
    data = data_str.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data)
    # optional to print on 24
    # print(future.result())
    future.add_done_callback(future_callback)
    future_list.append(future)
    count += 1
    if count % 10000 == 0:
        print(count)

# print(f"Published messages to {topic_path}.")
for future in futures.as_completed(future_list):
    continue

print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print(count)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")