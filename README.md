# Bond API by Jiří Hepnar
This project was created on Ubuntu so same commands may warry on other os

## How to start service
To start service you need to have `docker` and `docker-compose` installed  
Then it is simple:
```
> sudo docker-compose build
> sudo docker-compose up
```
## Or
Or you can use `Dockerfile.ci` and start it with your owns params:
```
sudo docker build -t bond-api -f Dockerfile.ci . && sudo docker run -it bond-api
```
You need to also copy `db/db.sqlite3` to `/www/bond-service/db/` or alter settings.py

## Interface
Then on http://127.0.0.1:8000/bond/api you shoud find Django REST framework web
interface and on http://127.0.0.1:8000/ shoud be some documentation

You can login with two differnt users:
 - `admin` with pasword `admin_password`
 - `common_user` with password `common_password`

## Imput data
You can add new emision in this format:
```
{
 "emmision_name": "Bond Valid ISIN",
 "isin": "CZ0003551251", # This isin is already in database for common_user
 "value": 10.0,
 "interest": 2.9,
 "purchase_date": "2024-06-16T12:00:00Z",
 "maturity_date": "2044-06-16T12:00:00Z",
 "interest_payment_frequency": "Yearly"
}
```

## Bond detail
If you want to work(show, update, delete) with your bond, please use ISIN as bond_id  
Example:
```
http://127.0.0.1:8000/bond/detail/CZ0003551251/api
```

## User endpoint
You can find user endpoint here:
```
 http://127.0.0.1:8000/bond/user/2/api
```
