from flask import Flask, render_template, request
import RPi.GPIO as gpio


# Pins for relay lines
relay1 = 0
relay2 = 1
relay3 = 2
relay4 = 3

# Setup GPIO lines
gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def home():
	if request.method == 'POST':
		if 'on' in request.form:
			print('on')	
		elif 'off' in request.form:
			print('off')
		elif 'thirty' in request.form:
			print('30 minutes')
		elif 'hour' in request.form:
			print('one hour')
		elif 'twohour' in request.form:
			print('two hours')

	return render_template('home.html')


if __name__ == '__main__':
	app.run(debug = True)
