from datetime import date, datetime, timedelta, timezone
import requests
import Dispense

def read_weather_key():
	#Getting weather key
	with open('secret.txt', 'r') as read:
		lines = read.readlines()
		read.close()
		return lines[0].strip()

def read_location():
	#Getting location
	with open('location.txt', 'r') as read:
		lines = read.readlines()
		read.close()
		return lines[0].strip()

weather_key = read_weather_key()
location = read_location()
able_to_water = True
down = False
retry = False
day_watered = ""
rain_history = []
current_rain = 0
rain_forecast = []
log = [None, None, None]


def update_log(new_entry):
	for index in range(2):
		log[index] = log[index + 1]
	log[-1] = new_entry

def update_dispense_log(new_entry):
	#Writing how much water was dispensed to file
	with open('dispense_log.txt', 'a') as read:
		read.write(str(datetime.now().strftime("%D")) + " - " + str(new_entry) + "\n")
		read.close()

def update_past_weather_log(new_entry):
	#Writing the rainfall to the file
	with open('past_weather.txt', 'a') as read:
		read.write(str(datetime.now().strftime("%D")) + " - " + str(new_entry) + "\n")
		read.close()

def create_lists():
	global rain_history, current_rain, rain_forecast, down
	#Checking to see if the server is up
	test = requests.get("https://api.darksky.net/forecast/" + weather_key + location)
	if test.status_code != 200:
		down = True
		return False
	#Resetting lists
	rain_history = []
	current_rain = 0
	rain_forecast = []
	#Historical rainfall
	for x in range(7, 0, -1):
		past_day = str(date.today() - timedelta(days=x))
		dt = datetime(int(past_day[:4]), int(past_day[5: 7]), int(past_day[8: 10]))
		timestamp = dt.replace(tzinfo=timezone.utc).timestamp() + 82800
		response = requests.get("https://api.darksky.net/forecast/" + weather_key + location + "," + str(int(timestamp)) + "?units=si")
		if response.status_code == 200:
			json = response.json()
			try:
				rain_history.append(json['daily']['data'][0]['precipIntensity'] * 24)
			except:
				rain_history.append(0)
		else:
			return False
	#Current and future rainfall
	for x in range(0, 6):
		if x == 0:
			response = requests.get("https://api.darksky.net/forecast/" + weather_key + location + "?units=si")
			print("current")
			if response.status_code == 200:
				json = response.json()
				try:
					current_rain = json['daily']['data'][0]['precipIntensity'] * 24
					update_past_weather_log(current_rain)
				except:
					current_rain = 0
			else:
				return False
		else:
			future_day = str(date.today() + timedelta(days=x))
			dt = datetime(int(future_day[:4]), int(future_day[5: 7]), int(future_day[8: 10]))
			timestamp = dt.replace(tzinfo=timezone.utc).timestamp() + 82800
			response = requests.get("https://api.darksky.net/forecast/" + weather_key + location + "," + str(int(timestamp)) + "?units=si")
			if response.status_code == 200:
				json = response.json()
				try:
					rain_forecast.append(json['daily']['data'][0]['precipIntensity'] * 24)
				except:
					rain_forecast.append(0)
			else:
				return False

def calculate():
	historical_average = 0
	future_average = 0
	log_average = 0

	for rainfall in rain_history:
		historical_average += rainfall
	historical_average /= len(rain_history)

	for rainfall in rain_forecast:
		future_average += rainfall
	future_average /= len(rain_forecast)


	for dispensed in log:
		if dispensed is not None:
			log_average += dispensed
	log_average /= len(log)

	total_average = (historical_average + future_average) / 2
	baseline = 38.1 - current_rain
	amount = 0

	if historical_average < 38.1:
		if future_average < 38.1:
			if baseline <= 0:
				if log_average > 19.05:
					amount += 38.1 - total_average
				else:
					amount += 38.1
			else:
				if log_average > 19.05:
					amount += 38.1 - total_average + baseline
				else:
					amount += 38.1 + baseline
		else:
			if baseline <= 0:
				if log_average > 13:
					pass
				else:
					amount += 19.05
			else:
				if log_average > 19.05:
					amount += baseline
				else:
					amount += 19.05 + baseline
	else:
		if future_average < 38.1:
			if baseline <= 0:
				if log_average > 19.05:
					amount += 19.05
				else:
					amount += 38.1
			else:
				if log_average > 19.05:
					amount += baseline
				else:
					amount += baseline + 19.05
		else:
			if baseline <= 0:
				if log_average > 19.05:
					pass
				else:
					pass
			else:
				if log_average > 19.05:
					amount += baseline
				else:
					amount += baseline
	update_log(amount)
	update_dispense_log(amount)

	#It takes the pump 4 seconds to dispense 5mL of water
	seconds = (amount * 4) / 5
	return seconds

def main():
	global retry, day_watered

	current_time = int(datetime.now().strftime("%H"))
	if retry == False and day_watered != datetime.now().strftime("%D") and current_time == 14:
		make_lists = create_lists()
		if make_lists == False:
			retry = True
			return
		else:
			#Setting day_watered stops the program from calling the calculate function over and over again at 2PM
			day_watered = datetime.now().strftime("%D")
			calc = calculate()
			if type(calc) == int or type(calc) == float:
				Dispense.dispense(calc)
			else:
				print("Error - Seconds is not type int or float")

	if retry:
		while True:
			remake_lists = create_lists()
			if remake_lists == False:
				time.sleep(600)
			else:
				retry = False
				return

while(True):
	main()
