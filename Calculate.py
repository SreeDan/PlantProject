from datetime import date, datetime, timedelta, timezone
import Dispense

startup = True
rain_history = []

def start():
	for x in range(7, 0, -1):
		past_day = str(date.today() - timedelta(days=x))
		dt = datetime(int(past_day[:4]), int(past_day[5: 7]), int(past_day[8: 10]))
		timestamp = dt.replace(tzinfo=timezone.utc).timestamp() + 82800
		response = requests.get("https://api.darksky.net/forecast/51c1013c03cd9cb1126fc4c22944d03d/40.7127,-74.0059," + str(int(timestamp)))
		json = response.json()
		rain_history.append(json['daily']['data'][0]['precipIntensity'] * 24)
	startup = False

def current():
	
