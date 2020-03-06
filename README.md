


# Quickstart

1. sync the logs u want locally

First download the logs you want.. EG:

```shell
export YEAR=2020
export MONTH=03
export DAY=06
export HOUR=16
mkdir -p ./logs/${YEAR}/${MONTH}/${DAY}/
aws s3 sync \
  s3://alb-logs-mt1/api-alb/AWSLogs/008815156580/elasticloadbalancing/us-east-1/${YEAR}/${MONTH}/${DAY}/ \
  ./logs/${YEAR}/${MONTH}/${DAY}/ \
  --exclude="*" \
  --include "*gateway*${YEAR}${MONTH}${DAY}T${HOUR}*"
```

2. `docker-compose up`

3. parse logs into elastic

```
find ./logs/${YEAR}/${MONTH}/${DAY} -type f -name "*.gz" -exec ./main.py -f {} \;
```





# setup your dev env

## elastic+kibana

1. get es + kibana data dir ready.. we need it owned by 1000:0

```
mkdir data-elasticsearch
sudo chmod g+rwx data-elasticsearch
sudo chown -R 1000:0 data-elasticsearch
```

2. `docker-compose up`

3. disable kibana telemetry


once its up.. u can disable telemetry like so:

```
curl -v http://localhost:5601/api/telemetry/v2/optIn \
  -H "kbn-version: 7.6.0" \
  -H "Accept: application/json, text/plain, */*" \
  -H "Content-Type: application/json;charset=utf-8" \
  --data '{"enabled":false}'
```


## python venv (optional)
1. create a python venv in `localenv` dir

```
python3 -m venv localvenv
```


2. activate the venv

(or use `direnv allow`)

```
source localvenv/bin/activate
```


3. install the deps

```
pip install --upgrade pip
pip install -r requirements.txt
```

4. write code

5. don't forget to freeze deps

```
pip freeze --path ./localvenv/lib/python3.8/site-packages > requirements.txt
```


