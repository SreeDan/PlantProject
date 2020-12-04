from datetime import date, datetime, timedelta, timezone
import Dispense

def read_weather_key():
	with open('secret.txt', 'r') as read:
		lines = read.readlines()
		return lines[0].strip()

weather_key = read_weather_key()
able_to_water = True
rain_history = []
current_rain = 0

def create_lists():
	#Historical rainfall
	for x in range(7, 0, -1):
		past_day = str(date.today() - timedelta(days=x))
		dt = datetime(int(past_day[:4]), int(past_day[5: 7]), int(past_day[8: 10]))
		timestamp = dt.replace(tzinfo=timezone.utc).timestamp() + 82800
		response = requests.get("https://api.darksky.net/forecast/" + weather_key + "/40.7127,-74.0059," + str(int(timestamp)))
		json = response.json()
		rain_history.append(json['daily']['data'][0]['precipIntensity'] * 24)
	#Current and future rainfall
	for x in range(0, 6):
		if x == 0:
			response = requests.get("https://api.darksky.net/forecast/" + weather_key + "/40.7127,-74.0059")
			json = response.json()
			current_rain = json['daily']['data'][0]['precipIntensity'] * 24
		else:
			future_day = str(date.today() + timedelta(days=x))
			dt = datetime(int(future_day[:4]), int(future_day[5: 7]), int(future_day[8: 10]))
			timestamp = dt.replace(tzinfo=timezone.utc).timestamp() + 82800
			response = requests.get("https://api.darksky.net/forecast/51c1013c03cd9cb1126fc4c22944d03d/40.7127,-74.0059," + str(int(timestamp)))
			json = response.json()
			rain_forcast.append(json['daily']['data'][0]['precipIntensity'] * 24)

def calculate():
	#

def main():
	current_time = int(datetime.now().strftime("%H"))
	if able_to_water and current_time == 14:
		calculate()


while(True):
	main()
