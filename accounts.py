# python accounts.py -i ../../data/twitter-creator.json -d regular -f 1
# python accounts.py -i ../../data/twitter-creator.json -d proxy -f 1

import sys
import time
import getopt
import simplejson
from selenium import webdriver
from SeleniumHelper import SeleniumHelper

class TwitterCreator(SeleniumHelper):

	MOBILE_URL_CREATE = 'https://mobile.twitter.com/signup?type=email'
	MOBILE_FIELD_SIGN_UP_NAME = '#oauth_signup_client_fullname'
	MOBILE_FIELD_SIGN_UP_EMAIL = '#oauth_signup_client_phone_number'
	MOBILE_FIELD_SIGN_UP_PASSWORD = '#password'
	MOBILE_FIELD_SIGN_UP_USERNAME = '#custom_name'
	MOBILE_BUTTON_SKIP_PHONE = '.signup-skip input'
	MOBILE_BUTTON_INTERESTS = 'input[data-testid="Button"]'

	DESKTOP_URL_CREATE = 'https://twitter.com/signup'
	DESKTOP_URL_SKIP = 'https://twitter.com/account/add_username'
	DESKTOP_URL_MAIN = 'https://twitter.com'
	DESKTOP_FIELD_SIGN_UP_NAME = '#full-name'
	DESKTOP_FIELD_SIGN_UP_EMAIL = '#email'
	DESKTOP_FIELD_SIGN_UP_PASSWORD = '#password'
	DESKTOP_FIELD_SIGN_UP_USERNAME = '#username'
	DESKTOP_FIELD_SIGN_UP_PHONE = '#phone_number'
	DESKTOP_FIELD_SIGN_UP_CODE = '#code'
	DESKTOP_FIELD_SIGN_UP_SUGGESTION = '.suggestions > ul:nth-child(2) > li:nth-child(1) > button:nth-child(1)'	
	DESKTOP_FIELD_LOGOUT = '#signout-form'
	DESKTOP_BUTTON_SKIP_PHONE = '.signup-skip input'
	DESKTOP_BUTTON_CALL_ME = 'input[name="call_me"]'
	DESKTOP_BUTTON_INTERESTS = 'input[data-testid="Button"]'

	DESKTOP_PAGE_CONTAINER = '#page-container'
	DESKTOP_PAGE_PHONE = '.PageContainer'
	DESKTOP_PAGE_INI = '#doc'


	def mobileCreateUser(self, row):
		self.loadPage(self.DESKTOP_URL_CREATE)
		self.waitAndWrite(self.DESKTOP_FIELD_SIGN_UP_NAME, row['name'])
		self.submitForm(self.selectAndWrite(self.DESKTOP_FIELD_SIGN_UP_EMAIL, row['email']))
		self.submitForm(self.waitAndWrite(self.DESKTOP_FIELD_SIGN_UP_PASSWORD, row['password']))
		self.clickSelector(self.DESKTOP_BUTTON_SKIP_PHONE)
		self.submitForm(self.waitAndWrite(self.DESKTOP_FIELD_SIGN_UP_USERNAME, row['username']))
		self.waitAndClick(self.DESKTOP_BUTTON_INTERESTS)
		#main_content > div.footer > form > input
		time.sleep(9999)
		# self.submitForm()

	def desktopCreateUser(self, row):
		self.loadPage(self.DESKTOP_URL_CREATE)
		self.waitAndWrite(self.DESKTOP_FIELD_SIGN_UP_NAME, row['name'])
		self.selectAndWrite(self.DESKTOP_FIELD_SIGN_UP_EMAIL, row['email'])
		self.submitForm(self.selectAndWrite(self.DESKTOP_FIELD_SIGN_UP_PASSWORD, row['password']))
		self.waitShowElement(self.DESKTOP_PAGE_CONTAINER)
		self.loadPage(self.DESKTOP_URL_SKIP)
		self.submitForm(self.waitAndWrite(self.DESKTOP_FIELD_SIGN_UP_USERNAME, row['username']))
		self.waitShowElement(self.DESKTOP_PAGE_CONTAINER)
		self.loadPage(self.DESKTOP_URL_MAIN)
		time.sleep(9999)

	def desktopCreateUserPhone(self, row):
		self.loadPage(self.DESKTOP_URL_CREATE)
		self.waitAndWrite(self.DESKTOP_FIELD_SIGN_UP_NAME, row['name'])
		self.selectAndWrite(self.DESKTOP_FIELD_SIGN_UP_EMAIL, row['email'])
		self.submitForm(self.selectAndWrite(self.DESKTOP_FIELD_SIGN_UP_PASSWORD, row['password']))
		self.submitForm(self.waitAndWrite(self.DESKTOP_FIELD_SIGN_UP_PHONE, row['phone']))
		row['code'] = raw_input('Code: ')
		self.submitForm(self.waitAndWrite(self.DESKTOP_FIELD_SIGN_UP_CODE, row['code']))
		self.waitAndClick(self.DESKTOP_FIELD_SIGN_UP_SUGGESTION)
		self.submitFormSelector(self.DESKTOP_FIELD_SIGN_UP_USERNAME)
		self.waitShowElement(self.DESKTOP_PAGE_CONTAINER)
		self.loadPage(self.DESKTOP_URL_MAIN)
		self.submitForm(self.waitShowElement(self.DESKTOP_FIELD_LOGOUT))
		self.waitShowElement(self.DESKTOP_PAGE_INI)

	def start(self, callbacks, inputFile, fromRow, toRow, driverType):
		try:
			rows = simplejson.loads(open(inputFile).read())
			numElements = len(rows)
		except:
			numElements = 0
		if numElements > 0:
			if toRow == -1:
				toRow = numElements
			else:
				if toRow > numElements:
					toRow = numElements
			fromRow -= 1
			if fromRow < numElements:
				self.driver = self.getWebdriver(driverType)
				for numRow in range(fromRow, toRow):
					row = rows[numRow]
					print('Processing row: ' + str(numRow))
					for callback in callbacks:
						callback(row)
					print('Processed.')
				self.close()
			else:
				print('Index out of bounds')
		else:
			print('Data could not be extracted')

	def getWebdriver(self, driverType):
		if driverType == 'proxy':
			profile = webdriver.FirefoxProfile()
			profile.set_preference( "network.proxy.type", 1 )
			profile.set_preference( "network.proxy.socks", "127.0.0.1" )
			profile.set_preference( "network.proxy.socks_port", 9150 )
			profile.set_preference( "network.proxy.socks_remote_dns", True )
			profile.set_preference( "places.history.enabled", False )
			profile.set_preference( "privacy.clearOnShutdown.offlineApps", True )
			profile.set_preference( "privacy.clearOnShutdown.passwords", True )
			profile.set_preference( "privacy.clearOnShutdown.siteSettings", True )
			profile.set_preference( "privacy.sanitize.sanitizeOnShutdown", True )
			profile.set_preference( "signon.rememberSignons", False )
			profile.set_preference( "network.cookie.lifetimePolicy", 2 )
			profile.set_preference( "network.dns.disablePrefetch", True )
			profile.set_preference( "network.http.sendRefererHeader", 0 )
			profile.set_preference( "javascript.enabled", False )
			profile.set_preference( "permissions.default.image", 2 )
			return webdriver.Firefox(profile)
		elif driverType == 'headless':
			return webdriver.PhantomJS()
		else:
			return webdriver.Firefox()

def main(argv):
	fromRow = 1
	toRow = -1
	inputFile = None
	driverType = 'proxy'
	opts, args = getopt.getopt(argv, "f:t:i:d:")
	if opts:
		for o, a in opts:
			if o in ("-f"):
				fromRow = int(a)
			elif o in ("-t"):
				toRow = int(a)
			elif o in ("-i"):
				inputFile = a
			elif o in ("-d"):
				driverType = a
	while not inputFile:
		inputFile = raw_input('Input file path: ')
	creator = TwitterCreator()
	print('Process started')
	creator.start(callbacks=[creator.desktopCreateUserPhone], inputFile=inputFile, fromRow=fromRow, toRow=toRow, driverType=driverType)
	print('Process ended')

if __name__ == "__main__":
    main(sys.argv[1:])