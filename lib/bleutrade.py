#
#
# Python implementation of the Bleutrade API
#
# See https://bleutrade.com/help/API for more information
#
# Copyright (c) 2016 Martin Albrecht <iwuerstchen@gmail.com>
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
#
import urllib2
import json
import hmac
import hashlib
import time


#
# Bleutrade API exception class
#
class BleutradeException(Exception):
	pass


#
# Bleutrade API class
#
class Bleurtrade:
	#
	# Constructor
	#
	def __init__(self, key=None, secret=None):
		self.baseURL = 'https://bleutrade.com/api/v2/'
		self.apiKey = key
		self.apiSecret = secret

	#
	# Error funciton to raise an exception with an error message
	#
	def __error(self, message):
		raise BleutradeException('Bleurtrade API error: ' + message)

	#
	# Fetch JSON data from API and return it as a dictionary
	#
	def __getjson(self, uri, private = False):
		req = urllib2.Request(uri)

		if private and not self.apiSecret:
			self.__error('API key and secret are required for this method')

		if private:
			sign = hmac.new(self.apiSecret, uri, hashlib.sha512).hexdigest()
			req.add_header('apisign', sign)

		r = urllib2.urlopen(req)
		if not r:
			self.__error('Cannot load API URL')

		j = json.loads(r.read())
		if not j["success"] or j["success"] is "false":
			self.__error("Error in fetching JSON: " + j["message"])

		return j

	#
	# Build request URL
	#
	def __build_url(self, method, query=''):
		uri = self.baseURL + method

		if self.apiKey:
			uri = uri + '?apikey=' + self.apiKey + '&nonce=' + \
				  str(time.time()).split('.')[0]

		if query:
			return uri + '&' + query
		else:
			return uri

	#
	# Build a query string
	#
	def __build_query(self, params):
		q = ''

		for key, value in params.iteritems():
			q = q + '&' + str(key) + '=' + str(value)

		return q

	#
	# Check given order type
	#
	def __chk_order_type(self, t):
		valid = ['ALL', 'BUY', 'SELL']
		if t not in valid:
			self.__error('Invalid order type')

		return str(t)

	#
	# Check given order status
	#
	def __chk_order_status(self, s):
		valid = ['ALL', 'OK', 'OPEN', 'CANCELED']
		if s not in valid:
			self.__error('Invalid order status')

		return str(s)

	#
	# Check the given period string
	#
	def __chk_period(self, p):
		valid = ['1m', '2m', '3m', '4m', '5m', '6m', '10m', '12m', '15m',
				 '20m', '30m', '1h', '2h', '3h', '4h', '6h', '8h', '12h',
				 '1d']

		if p not in valid:
			self.__error('Invalid period')

		return str(p)

	#
	# Use to get the balance of all your coins
	#
	# currencies can be of type string or list. If type is string all
	# currencies should be joined by a semicolon (e.g. "DOGE;BTC") or
	# just "ALL" for all currencies ("ALL" is default, if paramter is omitted).
	# If type is list every item in the list must be a currency name:
	#   currencies = ['DOGE', 'BTC']
	#
	def get_balances(self, currencies='ALL'):
		if type(currencies) == list:
			currencies = ';'.join(currencies)

		q = self.__build_query({'currencies': currencies})
		return self.__getjson(self.__build_url('account/getbalances', q), True)

	#
	# Get a list of all coins traded
	#
	def get_currencies(self):
		return self.__getjson(self.__build_url('public/getcurrencies'))

	#
	# Get the list of all pairs traded
	#
	def get_markets(self):
		return self.__getjson(self.__build_url('public/getmarkets'))

	#
	# Used to get the current tick values for a market
	#
	# market is a string. Format must be a valid Bleutrade market
	# name (e.g. BTC_DOGE)
	#
	def get_ticker(self, market):
		return self.__getjson(self.__build_url('public/getticker',
												'&market=' + market))

	#
	# Used to get the last 24 hour summary of all active markets
	#
	def get_market_summaries(self):
		return self.__getjson(self.__build_url('public/getmarketsummaries'))

	#
	# Used to get the last 24 hour summary of specific market
	#
	# market is a string. Format must be a valid Bleutrade market
	# name (e.g. BTC_DOGE)
	#
	def get_market_summary(self, market):
		return self.__getjson(self.__build_url('public/getmarketsummary',
												self.__build_query({
													'market': market
												})))

	#
	# Loads the book offers specific market
	#
	# market is a string. Format must be a valid Bleutrade market
	# name (e.g. BTC_DOGE)
	# t is a string. Valid values are: (BUY | SELL | ALL)
	# depth is an int. The default is 20, maximum is undefined by API
	#
	def get_order_book(self, market, t='ALL', depth=20):
		q = self.__build_query({
			'market': market,
			'type': self.__chk_order_type(t),
			'depth': int(depth)
		})

		return self.__getjson(self.__build_url('public/getorderbook', q))

	#
	# Obtains historical trades of a specific market
	#
	# market is a string. Format must be a valid Bleutrade
	# market name (e.g. BTC_DOGE)
	# count is an int. Default is 20 and maximum is 200. Value will allways
	# be normalized to 200, if greater
	#
	def get_market_history(self, market, count=20):
		c = 200 if count > 200 else count
		q = self.__build_query({'market': market, 'count': c})

		return self.__getjson(self.__build_url('public/getmarkethistory', q))

	#
	# Use to list your open orders
	#
	def get_open_orders(self):
		return self.__getjson(self.__build_url('market/getopenorders'), True)

	#
	# Use to get the deposit address of specific coin.
	#
	# currency is a string. Format must be a valid currency
	# name (e.g. BTC, DOGE, LTC)
	#
	def get_deposit_address(self, currency):
		return self.__getjson(self.__build_url('account/getdepositaddress',
							   self.__build_query({'currency': currency})),
							   True)

	#
	# Use to withdraw their currencies to another wallet
	#
	# currency is a string. Format must be a valid currency
	# name (e.g. BTC, DOGE, LTC)
	# quantity is an int with the amount of coins to withdraw
	# address is a string. Must be a valid address hash
	#
	def withdraw(self, currency, quantity, address):
		q = self.__build_query({
			'currency': currency,
			'quantity': quantity,
			'address': address
		})

		return self.__getjson(self.__build_url('account/withdraw', q), True)

	#
	# Use to direct transfer their currencies to another user, without fees
	#
	# currency is a string. Format must be a valid currency
	# name (e.g. BTC, DOGE, LTC)
	# quantity is an int with the amount of coins to withdraw
	# address is a string. Must be a valid address hash
	#
	def transfer(self, currency, quantity, touser):
		q = self.__build_query({
			'currency': currency,
			'quantity': quantity,
			'touser': touser
		})

		return self.__getjson(self.__build_url('account/transfer', q), True)

	#
	# Use to get the data given order
	# orderid is an int holding the order id to get
	#
	def get_order(self, orderid):
		return self.__getjson(self.__build_url('account/getorder',
							   self.__build_query({'orderid': orderid})), True)

	#
	# Use for historical trades of a given order
	#
	# orderid is an int holding the order id
	#
	def get_order_history(self, orderid):
		return self.__getjson(self.__build_url('account/getorderhistory',
							   self.__build_query({'orderid': orderid})), True)

	#
	# Use for historical deposits and received direct transfers
	#
	def get_deposit_history(self):
		return self.__getjson(self.__build_url('account/getdeposithistory'),
							   True)

	#
	# Use for historical withdraw and sent direct transfers.
	#
	def get_withdraw_history(self):
		return self.__getjson(self.__build_url('account/getwithdrawhistory'),
							   True)

	#
	# Use to cancel an order
	#
	# orderid is an int with the order id
	#
	def cancel_order(self, orderid):
		return self.__getjson(self.__build_url('market/cancel',
							   self.__build_query({'orderid': orderid})), True)

	#
	# Use to send texts to chat
	#
	# text is a string holding the message to send to the chat
	def chat_send(self, text):
		return self.__getjson(self.__build_url('account/chatsend',
							   self.__build_query({'text': text})), True)


	#
	# Obtains candles format historical trades of a specific market
	# market is a string. Format must be a valid Bleutrade
	# market name (e.g. BTC_DOGE)
	# period is a string. Must be a valid time period
	# count is an int. Maximum is 999999, default is 1000
	# lasthours is an int. Default is 24 and the maximum is 720
	#
	def get_candles(self, market, period='1d', count=1000, lasthours=24):
		# Normalize count
		if count < 0:
			count = 0
		if count > 999999:
			count = 999999

		# Normalize lasthours
		if lasthours < 0:
			lasthours = 0
		if lasthours > 720:
			lasthours = 720

		q = self.__build_query({
			'market': market,
			'period': self.__chk_period(period),
			'count': count,
			'lasthours': lasthours
		})

		return self.__getjson(self.__build_url('public/getcandles', q))

	#
	# Use to list your orders
	#
	# market is a string. Format must be a valid Bleutrade
	# market name (e.g. BTC_DOGE) or ALL for all markets. If omitted "ALL" is
	# is used as default.
	# status is a string. Must be a valid order status
	# t is a string. Must be a valid order type
	#
	def get_orders(self, market='ALL', status, t):
		q = self.__build_query({
			'market': market,
			'status': self.__chk_order_status(status),
			'type': self.__chk_order_type(t)
		})

		return self.__getjson(self.__build_url('account/getorders', q), True)

