# Practice Demo Virtual Machine

The VM has a user, `mndemo`, password `mndemo` (same as the user). Said user is and Adminitrator, so it can execute any command via `sudo`.

Simply boot the machine, wait for the Ubuntu login to show up, and enter the above credentials. To see the demo, open the FireFox broswer.

## Practice Demo Machine Installation

These notes are only meant to explain how to install (or re-create) the demo machine; they are not necessary to run the demo itself.  

The machine running the practice demo (Washington DC, Dec. 10-11 2014) was a Windows machine. The present notes describe how the online version of the demo has been installed, but in practice all the software described here could be run on a Windows is OS X machine.

Operating system: we chose **Ubuntu Linux 12.04 LTS**, but any recent Linux distribution (RedHat, Fedora, Mint, CentOS, etc.) will work as well.

## Preliminary steps: dependencies

### Before anything else, make sure the system is up-to-date:

```shell
apt-get update
apt-get upgrade
```

### Install the basic C development tools and Python 2.7

```shell
sudo apt-get install build-essential python2.7
```

### Install CouchDB 1.6.1

Cut and paste the following (these instructions are  from https://launchpad.net/~couchdb/+archive/ubuntu/stable):

```shell
# install the ppa-finding tool for 12.04 release
sudo apt-get install python-software-properties -y  
# add the ppa
sudo add-apt-repository ppa:couchdb/stable -y
# install CouchDB
sudo apt-get install -V couchdb
# start via upstart
sudo start couchdb
```

### Install Oracle Java 8 (Java 7 would be fine as well)

```shell
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java8-installer
```

### Install [Elasticsearch](http://www.elasticsearch.org/)

Go to [Elasticsearch's website](http://www.elasticsearch.org/overview/elkdownloads/) and download the [DEB distrbution](https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.4.2.deb); install it with the following command:

```shell
sudo dpkg -i elasticsearch-1.4.2.deb
```

Install the following two plugins:

```shell
cd /usr/share/elasticsearch
./bin/plugin -install elasticsearch/elasticsearch-lang-python/2.4.1
./bin/plugin -install elasticsearch/elasticsearch-river-couchdb/2.4.1
```

Edit `/etc/elasticsearch.yml`. Add the following line at the end:

```shell
# Dynamic scripting support
script.disable_dynamic: false
```

Start Elasticsearch:

```shell
sudo service elasticsearch start
```

### Install development version of [IPython](http://ipython.org/)

Install `IPython` from its [GitHub repository](https://github.com/ipython/ipython#development-installation): follow instructions for the **Development installation**.


## _ICSI_ software

### Main repository

We assume that the contents of _ICSI_'s `metanetdev` source code release has been expanded in a suitable directory (for instance, `~/src`). So we `cd` to the `demo` subfolder of the `metanetdev` folder. Please refer to the main documentation (in the `metanetdev/docs` folder) for more information.

```shell
cd ~/src/metanetdev/demo
```

### Python packages

Also, make sure you have all the Python packages required by the main repository (the ones needed to run `m4detect` and `m4mapping`). The demo requires all of them, plus the following:

  * `nltk`
  * `ujson`
  * `couchdb`
  * `couchdbkit`
  * `pymongo`
  * `elasticsearch`
  * `bokeh`
  * `matplotlib`

Usually all packages can be installed via [`pip`](https://pypi.python.org/pypi/pip), but you may want to install the last one, [`matplotlib`](http://matplotlib.org/index.html), via the system package manager:

```shell
sudo apt-get install python-matplotlib
```

### Set up PYTHONPATH

Add demo source directory to `PYTHONPATH`:

```shell
export PYTHONPATH=$PYTHONPATH:$HOME/src/metanetdev/demo/src/python
```

### Load GMR Case study data

Assuming you are still under `~/src/metanetdev/demo`, issue the following command:

```shell
python -m gmr.load -t couchdbkit -l test_case -f "data/gmr2014.12.05T1/casestudy/Result*"
```

### Index the GMR data using Elasticsearch

```shell
# Create index
curl -XPUT 'http://localhost:9200/lms-test3'

# Create mappings
curl -XPUT 'http://localhost:9200/lms-test3/_mapping/lms3' -d '{
  "properties": {
    "id": {
      "type": "string",
      "index": "not_analyzed"
    },
    "cms": {
      "type": "string",
      "index": "not_analyzed"
    },
    "source-form": {
      "type": "string",
      "index": "not_analyzed"
    },
    "source-lemma": {
      "type": "string",
      "index": "not_analyzed"
    },
    "source-concepts": {
      "type": "string",
      "index": "not_analyzed"
    },
    "source-schemanames": {
      "type": "string",
      "index": "not_analyzed"
    },
    "source-schemafamilies": {
      "type": "string",
      "index": "not_analyzed"
    },
    "target-form": {
      "type": "string",
      "index": "not_analyzed"
    },
    "target-lemma": {
      "type": "string",
      "index": "not_analyzed"
    },
    "target-concept": {
      "type": "string",
      "index": "not_analyzed"
    },
    "target-schemaname": {
      "type": "string",
      "index": "not_analyzed"
    },
    "target-congroup": {
      "type": "string",
      "index": "not_analyzed"
    },
    "target-schemafamily": {
      "type": "string",
      "index": "not_analyzed"
    },
    "text" : {
      "type": "string"
    }
  }
}'

# Start automatic indexing
PUT 'http://localhost:9200/_river/test_docs_case_study/_meta' -d '{
  "type" : "couchdb",
  "couchdb" : {
    "host" : "localhost",
    "port" : 5984,
    "db" : "test_docs_case_study",
    "filter" : null,
    "script" : "# =====================================================================\n# Elasticsearch\n# ---------------------------------------------------------------------\n# Make index for 'lms' key; no index if no lms key is present\n# ---------------------------------------------------------------------\n\ndef make_index(ctx):\n    doc = ctx['doc']\n    if 'lms' in doc:\n        newDoc = dict()\n        lms = doc['lms']\n#         newDoc['id'] = doc['_id'].replace(':', '_')\n#         Setup id as unanalyzed:\n#         PUT /lms-index/_mapping/lm\n#         {\n#           \"properties\" : {\n#             \"id\" : {\n#               \"type\" :    \"string\",\n#               \"index\": \"not_analyzed\"\n#               \n#             }\n#           }\n#         }\n        newDoc['id'] = doc['_id']\n        if 'perspective' in doc:\n            newDoc['perspective'] = doc['perspective']\n\n        # Include sentence \n        newDoc['text'] = doc['text']\n                    \n        for lm in doc['lms']:\n            newDoc['score'] = lm['score']\n            newDoc['cms']   = [c.split('VettedMetaphor_')[1] for c in lm['cms']]\n\n            # Source\n            source = lm['source']\n            newDoc['source-form']           = source['form']\n            newDoc['source-lemma']          = source['lemma']\n            newDoc['source-concepts']       = source['concepts']\n            newDoc['source-schemanames']    = source['schemanames']\n            newDoc['source-schemafamilies'] = source['schemafamilies']\n            newDoc['source-coreness']       = [m['coreness'] for m in source['mappings']]\n\n            # Target\n            target = lm['target']\n            newDoc['target-form']           = target['form']\n            newDoc['target-lemma']          = target['lemma']\n            newDoc['target-concept']        = target['concept']\n            newDoc['target-schemaname']     = target['schemaname']\n            newDoc['target-congroup']       = target['congroup']\n            newDoc['target-schemafamily']   = target['schemafamily']\n\n        return newDoc\n    else:\n        return None\n\nlms = make_index(ctx)\nif lms != None:\n    ctx['doc'] = lms\nelse:\n    ctx['ignore'] = True\n",
    "script_type" : "python"
  },
  "index" : {
    "index" : "lms-test3",
    "type" : "lms3",
    "bulk_size" : "10000",
    "bulk_timeout" : "10000ms"
  }
}'
```

After the above, `Elasticsearch` will start indexing the `JSON` data in the `CouchDB` database. You should ready to start the `IPython` notebook server and run queries.

### Start the IPython notebook server

```shell
ipython notebook --notebook-dir=~/src/metanetdev/demo/src/demo
```

This should open a browser to your machine at [`http://localhost:8888`](http://localhost:8888). You should be able to open the notebook named `Practice Case Demonstration Live Query Tool.ipynb`; follow the instructions to reproduce the analytics for the presentation.

### HTML Presentation

An expanded version of the presentation given in Washington is contained under `~/src/metanetdev/demo/src/html/presentation`; point your browser to that location to see it.