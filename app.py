from flask import Flask, render_template, request
try:
	import RPi.GPIO as gpio
except:
	print('RPi.GPIO not found')
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import traceback
import datetime as dt
import json

############## PARAMETERS #############
# Pins for relay lines
relays = [2, 3, 14, 15]
fan = 2

# Set if debugging is active
debugSet = False
#######################################
#######################################

# Setup logging
logger = logging.getLogger('mainLog')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('log.log')
fh.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(lineno)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
sh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)

# Setup scheduler
s = BackgroundScheduler(misfire_grace_time=60, max_instances=1, timezone='America/New_York')
s.start()
logger.info('Scheduler setup')

# Setup GPIO lines
try:
	gpio.setmode(gpio.BCM)
	gpio.setwarnings(False)
	for i in relays:
		gpio.setup(i, gpio.OUT)
	gpio.output(fan, 1) # Start the fan off
except:
	logger.error('Could not setup GPIO')
	logger.error(traceback.print_exc())

app = Flask(__name__)

# Define function to turn off the fan gpio line
def turnOff():
	logger.info('Turning off')
	# Try to remove the turn off job
	try:
		s.remove_job('turnoff')
		logger.debug('Removed scheduler job')
	except:
		logger.debug("Didn't find a scheduler job")
		pass
	
	try:
		gpio.output(fan, 1)
		logger.info("Turned off fan")
	except:
		logger.error("Could not turn off fan GPIO")
		logger.error(traceback.print_exc())

# Define function to turn on fan gpio line
def turnOn():
	logger.info("Turning on")

	try:
		gpio.output(fan, 0)
		logger.info("Turned on fan")
	except:
		logger.error("Could not turn on fan GPIO")

# Define function to start a timer
def setupTimer(minutes):
	# Check if there is already a timer running
	if(len(s.get_jobs()) > 0):
		s.remove_job('turnoff')

	s.add_job(turnOff, 'interval', minutes=minutes, id='turnoff')
	logger.info('Set timer for ' + str(minutes) + ' minutes')

@app.route('/', methods=['POST', 'GET'])
def home():
	if request.method == 'POST':
		if 'on' in request.form or 'on' in str(request.data):
			turnOn() # Turn on the fan

		elif 'off' in request.form or 'off' in str(request.data):
			turnOff() # Turn off the fan

		elif 'thirty' in request.form or 'thirty' in str(request.data):
			turnOn() # Turn on the fan
			setupTimer(30) # Start a timer for 30 minutes

		elif 'hour' in request.form or 'hour' in str(request.data):
			turnOn() # Turn on the fan
			setupTimer(60) # Start a timer for one hour

		elif 'twohour' in request.form or 'twohour' in str(request.data):
			turnOn() # Turn on the fan
			setupTimer(120) # Start a timer for two hours

	# Print out the reamining time on any timers on the website
	try:
		timeToRun = s.get_jobs()[0].next_run_time
		now = dt.datetime.now(dt.timezone.utc)
		diff = (timeToRun - now).seconds + 1
		logger.debug('Time difference ' + str(diff))
		timeLeft='Turning off at ' + dt.datetime.strftime(timeToRun, '%I:%M') + ' in ' + str(int((diff/3600.0)))  + ' hours and ' + str(int(round((diff%3600)/60))) + ' minutes.'
	except:
		timeLeft='No timer set'
	return render_template('home.html', timeLeft=timeLeft)


if __name__ == '__main__':
	app.logger.addHandler(fh)
	app.run(debug = debugSet, host='0.0.0.0')
