# Automatic pipeline for collecting Telegram multimodal data

Note: This code uses Telegram API in order to get the data. Make sure you have requested access before starting. For detailed instructions on how to request the access to the Telegram API, and how to generate the needed tokens, have a look at: https://core.telegram.org/

## Installation 

Create and activate a virtual environemnt. Then, install all the required packages
 ```
 pip install -r /path/to/requirements.txt
```

## API token 
Create a .yaml file called ***config.yaml*** to store your keys and other configuracion variables. It should have the following strcuture: 

```
root_path: 'my_path'
channels_file: 'my_channels_list.txt'
api_id: 'my_api_id'
api_hash: 'my_api_hash'
test: 'my_test'
test_public_key: 'my_test_key'
prod: 'my_prod'
prod_public_key: 'my_prod_key'
phone: 'my_phone'
user: 'my_user'
```

Remember to keep this file on the .gitignore since it contains sensible information. Alternativetly, you could use another method to store your API keys. Feel free to adapt the code.


## Configuration
In addition you will have to provide a .txt file with a list of users id that you would like to start to get data from. Here is an example:

```
nocovidvaccines
UNVACCINATE
OneRepublicNetwork
TheUnvaccinatedArmsChat
SeniorChaplain
HVUNetwork
ChlorineDioxideTestimonies
Truthers4victory
TheDonsNightShift
Seventeen76777CHAT
CampQueenKong
unvaccinatedDOTonline
```

## Running the code
Note that the code is designed to run in a daily basis. When running for the first time you will get data from the day before running the script. For testing, inside your virtual environment, just simply run:
```
python3 get_telegram_data.py
```

If you want the collection to run everyday, just add the command into a cronjob.

## Files structure