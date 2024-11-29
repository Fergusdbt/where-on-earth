import requests
from cs50 import SQL

db = SQL("sqlite:///whereonearth.db")

# To update TABLE 'countries' in whereonearth.db, run the following commands...
#1 DELETE FROM countries; (in sqlite3)
#2 UPDATE sqlite_sequence SET seq=0 WHERE name ='countries'; (in sqlite3)
#3 python countries.py

data = requests.get('https://restcountries.com/v3.1/all?fields=cca3,name,flags,region,unMember')
countries = data.json()
            
for country in countries:
    code = country["cca3"]
    name = country["name"]["common"]
    flag = country["flags"]["png"]
    region = country["region"]
    unMember = country["unMember"]

    db.execute("INSERT INTO countries (code, name, flag, region, unMember) VALUES (?, ?, ?, ?, ?)", code, name, flag, region, unMember)