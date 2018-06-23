from flask import Flask, render_template, request
try:
	import RPi.GPIO as gpio
except:
	print('RPi.GPIO not found')
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# Setup logging
logger = logging.getLogger('mainLog')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('log.log')
fh.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(lineno)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
sh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)

# Setup scheduler
s = BackgroundScheduler(misfire_grace_time=60, max_instances=1, timezone='America/New_York')
s.start()
logger.info('Scheduler setup')

# Pins for relay lines
relays = [2, 3, 14, 15]
fan = 2

# Set if debugging is active
debugSet = True
# Setup GPIO lines
try:
	gpio.setmode(gpio.BCM)
	gpio.setwarnings(False)
	for i in relays:
		gpio.setup(i, gpio.OUT)
except:
	logger.error('Could not setup GPIO')

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
		logger.into("Turned off fan")
	except:
		logger.error("Could not turn off fan GPIO")

# Define function to turn on fan gpio line
def turnOn():
	logger.info("Turning on")

	try:
		gpio.output(fan, 0)
		logger.info("Turned on fan")
	except:
		logger.error("Could not turn on fan GPIO")

@app.route('/', methods=['POST', 'GET'])
def home():
	s.print_jobs()
	if request.method == 'POST':
		if 'on' in request.form:
			turnOn()

		elif 'off' in request.form:
			turnOff()

		elif 'thirty' in request.form:
			turnOn()

			# Setup timer
			s.add_job(turnOff, 'interval', minutes=30, id='turnoff')
			logger.info('Set timer for 30 minutes')

		elif 'hour' in request.form:
			turnOn()

			# Setup timer
			s.add_job(turnOff, 'interval', hours=1, id='turnoff')
			logger.info('Set timer for 1 hour')

		elif 'twohour' in request.form:
			turnOn()

			# Setup timer
			s.add_job(turnOff, 'interval', hours=2, id='turnoff')
			logger.info('Set timer for 2 hours')

	return render_template('home.html')


if __name__ == '__main__':
	app.run(debug = debugSet, host='0.0.0.0')
