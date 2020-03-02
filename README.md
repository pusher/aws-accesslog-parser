


1. sync the logs u want locally

This little utility will download a specific hour.. `-t` format is `YYYYMMDD-HH`

```
./downloader.py -l mt1-api-gateway -t "20190229-06"
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


