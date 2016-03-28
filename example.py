#
# Example program how to use the Bleutrade python API
#
import sys
from bleutradeapi.bleutrade import *

try:
	# Fetch all markets
	json = Bleutrade().get_markets()
	print json

	# Fetch balances
	apiKey = 'YOUR_API_KEY'  # Replace with your API key
	apiSecret = 'YOUR_API_SECRET'  # Replace with your API secret
	currencies = ['DOGE', 'BTC', 'LTC']
	json = Bleurtrade(apiKey, apiSecret).get_balances(currencies)
	print json


except BleutradeException as e:
	print e
