#!/usr/local/bin/python3

import pymazda
import asyncio
import json
import argparse
import sys
import os

parser = argparse.ArgumentParser(description='MyMazda API tool')
parser.add_argument("--list", action='store_true', help="List all cars registered to your MyMazda account.")
parser.add_argument("--name", type=str, help="Car's defined name.")
parser.add_argument("--vin", type=str, help="Car's VIN.")
parser.add_argument("--car_id", type=str, help="Car's defined id number.")
parser.add_argument("--status", action='store_true', help="Return the status report from the vehicle.")
parser.add_argument("--engine", choices=["start", "stop"], type=str, help="Control the engine.")
parser.add_argument("--doors", choices=["lock", "unlock"], type=str, help="Control the door locks.")
parser.add_argument("--email", type=str, help="MyMazda account email adress.")
parser.add_argument("--password", type=str, help="MyMazda account password.")
parser.add_argument("--poi_name", type=str, help="Point of interest name.")
parser.add_argument("--poi_lat", type=float, help="Point of interest latitude.")
parser.add_argument("--poi_long", type=float, help="Point of interest longitude.")
if len(sys.argv) < 2:
	parser.print_help()
	sys.exit(1)

args = parser.parse_args()
config_file_path = os.path.join(os.path.dirname(__file__), "config.json")
if os.path.isfile(config_file_path):
	# read from the config
	with open(config_file_path) as conf_file:
		conf = json.load(conf_file)
		email = conf['email']
		password = conf['password']
		try:
			car_id = conf['car_id']
		except:
			car_id= ''
else:
	# look for config from args or env
	email = args.email
	password = args.password
	car_id = args.car_id
	if not email:
		email = os.getenv('mazda_api_email')
	if not password:
		password = os.getenv('mazda_api_password')
	if not car_id:
		car_id = os.getenv('mazda_api_car_id')
do_list = args.list
do_engine = args.engine
do_doors = args.doors
do_status = args.status
poi_name = args.poi_name
poi_lat = args.poi_lat
poi_long = args.poi_long
car_name = args.name
car_vin = args.vin

async def output_all_data() -> None:
	# Get list of vehicles from the API (returns a list)
	vehicles = await client.get_vehicles()
	print(json.dumps(vehicles, indent=2))
	
async def get_car_id() -> None:
	#data = json.loads(output_all_data())
	data = await client.get_vehicles()
	the_car_id = [ ]
	if car_name:
		for value in data:
			if value['nickname'].lower() == car_name.lower():
				the_car_id.append(value["id"])
	elif car_vin:
		for value in data:
			if value['vin'].lower() == car_name.lower():
				the_car_id.append(value["id"])
	elif car_id:
		the_car_id.append(car_id)
	else:
		print('No car identification method given.')
	
	# make sure we only have a single match
	if len(the_car_id) >= 2:
		print('Multiple matches found for vehicle identification.')
	else:
		return the_car_id[0]

async def control_engine(vehicle_id, action) -> None:
	if action == "start":
		# Start engine
		await client.start_engine(vehicle_id)
	elif action == "stop":
		# Stop engine
		await client.stop_engine(vehicle_id)
	else:
		print("Error: unknown action.")

async def control_locks(vehicle_id, action) -> None:
	# Initialize API client (MNAO = North America)
	client = pymazda.Client(email, password, "MNAO")
	if action == "lock":
		# Lock
		await client.lock_doors(vehicle_id)
	elif action == "unlock":
		# Unlock
		await client.unlock_doors(vehicle_id)
	else:
		print("Error: unknown action.")

async def output_car_data(vehicle_id) -> None:
	# Get and output vehicle status
	status = await client.get_vehicle_status(vehicle_id)
	#print(status)
	print(json.dumps(status, indent=2))

async def main_job() -> None:
	# print all the vehicles we have
	if do_list:
		await output_all_data()
		# Close the session
		await client.close()
		return
	
	# Get an ID and go to work
	car_id = await get_car_id()

	if poi_name:
		await client.send_poi(car_id, poi_lat, poi_long, poi_name)
		# Close the session
		await client.close()
		return

	if do_status:
		await output_car_data(car_id)
	elif do_engine:
		await control_engine(car_id, do_engine)
	elif do_doors:
		await control_locks(car_id, do_doors)
	else:
		print('No task specified.')

	# Close the session
	await client.close()

# sanity check for the bare minium input we need
if not email or not password:
	print('Missing email and/or password data.')
	parser.print_help()
	exit(2)
elif not car_id:
	print('Missing a car_id, which can be passed a number of ways.')
	parser.print_help()
	exit(2)

# Initialize API client (MNAO = North America)
client = pymazda.Client(email, password, "MNAO")

# Run the job
loop = asyncio.get_event_loop()
loop.run_until_complete(main_job())

