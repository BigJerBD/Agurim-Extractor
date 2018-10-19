Agurim Extractor
===============
this code contains multiple command line tool to help the user to manipulate data from [Agurim](http://mawi.wide.ad.jp/~agurim/). 


## Getting Started
These Instructions will allow to setup  the depedencies  and to learn how to run this extraction tool
### Prerequisites

to use this extract you must have the [Selenium Chrome Driver](http://chromedriver.chromium.org/)
installed to your machine. For that, download and install the most recent version.

Installing the Chrome Driver on Windows requires to set the Chrome Driver directory path into the 
PATH environement variable.


For the installation of the data in Elasticsearch you need to have 
an elastic search database installed. preferably with kibana to visualise the data
properlly .To install those tool follow these link
* [elasticsearch](https://www.elastic.co/downloads/elasticsearch)
* [kibana](https://www.elastic.co/downloads/kibana)


python3+ is also required

### Installing
Run in a terminal : 
```bash
pip install -r requirements.txt
```
and the python necessary python requirement will be installed
## Usage 


### agurim_fetcher

to run the script to import agurim data from the website to a csv format, 
from the root directory, call : 

```text
python agurim_fetcher/agurim_fetcher.py <arguments> 
```

usage specification : 

```text
usage: agurim_fetcher.py [-h] [-u URL] [-p PAIR_CSV] [--csv_dst CSV_DST]
                         [-s START_TIME] [-e END_TIME] [-i INTERVAL]
                         [-d DURATION] [-c {byte,packet}] [-v {addr,proto}]
                         [-n NFLOWS] [--show] [--skip_retry]
                         [--skip_csv_conversion]
                         dst

Agurim traffic data web fetcher

positional arguments:
  dst                   destination of the extracted files

optional arguments:
  -h, --help                                    show this help message and exit
  -u URL, --url URL                             url of agurim API (default: http://mawi.wide.ad.jp/~agurim/detail.html)
  -p PAIR_CSV, --pair_csv PAIR_CSV             csv of begin and end time to use for the fetching (default: None)
  -s START_TIME, --start_time START_TIME        starting unix timestamp of data fetching (default:1360249200)
  -e END_TIME, --end_time END_TIME              ending unix timestamp of data fetching (default:<most recent data>)
  -i INTERVAL, --interval INTERVAL              intervals for each point (default is minimum interval) (default: 600)
  -d DURATION, --duration DURATION              duration of a csv fetch (default: 86400)
  -c {byte,packet}, --criteria {byte,packet}    data type (default: byte)
  -v {addr,proto}, --view {addr,proto}          view mode (default: proto)
  -n NFLOWS, --nflows NFLOWS                    maximum number of flow in the received csv (default:9999)
  --show                                        show the browser while extracting data (default:False)
  --skip_retry                                  show the browser while extracting data (default:False)
  --csv_dst CSV_DST                             destination for csv_converted files  (default: dst file)
  --skip_csv_conversion                         skips the conversion of the files into a csv format (default: False)

```


### agurim_to_elastic

to run the script to import agurim csvs in a elastic database or in a ndjson format, 
from the root directory, call : 

```text
python agurim_to_elastic/agurim_to_elastic.py <arguments> 
```

the different arguments are listed bellow :

```text
usage: agurim_to_elastic.py [-h] [--ndjson_dst NDJSON_DST] [--index INDEX]
                            [--type TYPE] [--host HOST] [--port PORT]
                            [--chunk_size CHUNK_SIZE] [--no_progressbar]
                            [--no_id]
                            src {elastic,ndjson,both}

Transfer a folder of agurim csv to an elasticsearch database

positional arguments:
  src                       path to the agurim csv file folder
  {elastic,ndjson,both}     write output type

optional arguments:
  -h, --help                show this help message and exit
  --ndjson_dst NDJSON_DST   location to write the ndjson (default: None)
  --index INDEX             index where to put data in elastic (default: )
  --type TYPE               document type to be used with those data (default: )
  --host HOST               host to the elasticsearch url (default: localhost)
  --port PORT               host to the elasticsearch url (default: 9200)
  --chunk_size CHUNK_SIZE   chunk size for every bulk transaction (default: 3000)
  --no_progressbar          toggle off progress bar (default:False)
  --no_id                   toggle off datapoint ids (default:False)

```
note:: the index and the data type should be already present on elastic search. you can do it with a curl request like this one :

```bash
curl --request PUT \
     --url http://localhost:9200/<INDEX>\
     --header 'content-type: application/json' \
     --data '{"mappings": {
                "<TYPE>": {
                    "properties": {
                        "timestamp": {
                            "type": "date",
                            "format":"epoch_second"
                            }
                        }
                    }
                }	
            }'
```
you have to replace the TYPE and INDEX tag by the right one.

## References

* [Agurim](http://mawi.wide.ad.jp/~agurim/) - network traffic monitor based on flexible multi-dimensional flow aggregation
 using Japan's Wide Data
 
* [Selenium Chrome Driver](http://chromedriver.chromium.org/) - selenium driver used to automate web actions

* [Elastic.co](https://www.elastic.co/) - Open Source search and analytic tools

## Authors

* **Jérémie Bigras-Dunberry** - *Initial work* - Canadian NTT intern 




