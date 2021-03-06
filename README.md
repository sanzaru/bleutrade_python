# Bleutrade Python API 
Python client library implementation of the Bleutrade API

The object will return a dictionary containing the JSON to work with in your program.
For more information see: https://bleutrade.com/help/API

**NOTE:** The module is written for python version 2.7 and will surely not run on python 3 or versions below 2.7. A version for python3 will come later.

### Installation
Unix machines:

`sudo pip install bleutradeapi`

Windows:

`pip install bleutradeapi`


### Usage

```python
    from bleutradeapi.bleutrade import *

    # Fetch all markets
    json = Bleutrade().get_markets()
    print json
```
Here we fetch data for all markets. As this API method is a public function we don't need to provide any authentication data. Of course, you can always initiate an object and use it:

```python
  from bleutradeapi.bleutrade import *
  
  api = new Bleutrade()
  json = api.get_markets()
  ...
```

For private methods we do need to provide authentication data:
```python
  from bleutradeapi.bleutrade import *
  
	currencies = ['DOGE', 'BTC', 'LTC']
	json = Bleutrade('YOUR_API_KEY', 'YOUR_API_SECRET').get_balances(currencies)
	print json
```
