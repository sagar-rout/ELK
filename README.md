# ELK - distributed logging for services 

## Elasticsearch
It is an open source search and analytics engine based on [Apache Lucene](https://lucene.apache.org/). [Elasticsearch](https://www.elastic.co/what-is/elasticsearch) is centre for Elastic stack which contains tools like kibana, logstash and beats like metricbeat and filebeat.


## Logstash
Logstash is a light-weight, open-source, server-side data processing pipeline that allows you to collect data from a variety of sources, transform it on the fly, and send it to your desired destination. It is most often used as a data pipeline for Elasticsearch, an open-source analytics and search engine. Because of its tight integration with Elasticsearch, powerful log processing capabilities, and over 200 pre-built open-source plugins that can help you easily index your data, Logstash is a popular choice for loading data into Elasticsearch. I found this information from
(Amazon)[https://aws.amazon.com/elasticsearch-service/the-elk-stack/logstash/]


## Kibana
Kibana is an open-source data visualization and exploration tool used for log and time-series analytics, application monitoring, and operational intelligence use cases. It offers powerful and easy-to-use features such as histograms, line graphs, pie charts, heat maps, and built-in geospatial support. Also, it provides tight integration with Elasticsearch, a popular analytics and search engine, which makes Kibana the default choice for visualizing data stored in Elasticsearch. I found this information from (Amazon)[https://aws.amazon.com/elasticsearch-service/the-elk-stack/kibana/]

## Beats
It is lightweight tool to ship logs from client to elasticsearch. It can ship logs from console and files. In this example, We will use (filebeat)[https://www.elastic.co/guide/en/beats/filebeat/current/index.html]


```bash
docker run -d -p 9200:9200 -p 9300:9300 --name elasticsearch -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.10.1
```

```bash
docker run -d --link elasticsearch:elasticsearch -p 5601:5601 docker.elastic.co/kibana/kibana:7.10.1
```

In this example, we have one sample python (flask) based application and we are generating some 
random data. The (logs)[log_req.log] are in json format.

we have one stupid endpoint, which generates random student name and address using (Faker)[https://faker.readthedocs.io/en/master/].

```bash
curl -v http://localhost:5000/students?no_students=100
```

Below sample code will generate logs in the same directory.

```python
import json_logging, logging, sys, flask
from flask import jsonify, request
from faker import Faker
fake = Faker()

# Flask
app = flask.Flask(__name__)

# logging configuration
json_logging.init_flask(enable_json=True)
json_logging.init_request_instrument(app)

request_logger = json_logging.get_request_logger()
handler = logging.handlers.RotatingFileHandler(filename='log_req.log', maxBytes=5000000, backupCount=10)
handler.setFormatter(json_logging.JSONRequestLogFormatter())
request_logger.addHandler(handler)


@app.route('/')
def home():
    return jsonify({'Hello': 'World'})


@app.route('/students')
def students():
    no_students = request.args.get("no_students")
    if (no_students == None):
        return jsonify({'crazy': True})

    no_students = int(no_students)
    students = []
    for _ in range(no_students):
        students.append({'name': fake.name(), 'address': fake.address()})

    return jsonify(students)

@app.route('/movies')
def movies():
    movies = [
        'Inception',
        'Interstellar',
        'black hawk down',
        'cinderella man',
        'a beautiful mind'
    ]

    return jsonify(movies)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(5000))
```

Let's using filbeat agent to ship logs from log file to elasticsearch.

Filebeat config :

```bash
filebeat.inputs:

- type: log

  # Change to true to enable this input configuration.
  enabled: true

  # Paths that should be crawled and fetched. Glob based paths.
  paths:
    - /home/sagar/Desktop/ELK/log_req.log
  fields_under_root: true
  json.message_key : "message"
  json.keys_under_root: true
  # filestream is an experimental input. It is going to replace log input in the future.
- type: filestream

  # Change to true to enable this input configuration.
  enabled: false

  # Paths that should be crawled and fetched. Glob based paths.
  paths:
    - /var/log/*.log
  filebeat.config.modules:
  # Glob pattern for configuration loading
  path: ${path.config}/modules.d/*.yml
  fields_under_root: true  

  # Set to true to enable config reloading
  reload.enabled: false

# ======================= Elasticsearch template setting =======================

setup.template.settings:
  index.number_of_shards: 1
  index.number_of_replicas: 0
  #index.codec: best_compression
  #_source.enabled: false


# ---------------------------- Elasticsearch Output ----------------------------
output.elasticsearch:
  # Array of hosts to connect to.
  hosts: ["localhost:9200"]
```