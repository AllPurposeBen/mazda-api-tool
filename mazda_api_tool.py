#!/usr/local/bin/python3

import pymazda
import asyncio
import json
import argparse
import sys

parser = argparse.ArgumentParser(description='MyMazda API tool')
parser.add_argument("--list", action='store_true', help="List all cars registered to your MyMazda account.")
parser.add_argument("--car_id", type=str, help="vehicle ID of the vehicle you want to control.")
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
car_id=args.car_id
# if not car_id:
# 	exit(2)
do_engine = args.engine
do_doors = args.doors
email = args.email
password = args.password
if not email:
	email = os.getenv('mazda_api_email')
if not password:
	password = os.getenv('mazda_api_password')
do_list = args.list
poi_name = args.poi_name
poi_lat = args.poi_lat
poi_long = args.poi_long

async def output_all_data() -> None:
	# Get list of vehicles from the API (returns a list)
	vehicles = await client.get_vehicles()
	print(json.dumps(vehicles, indent=2))

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
	if do_list:
		await output_all_data()
		# Close the session
		await client.close()
		return

	if poi_name:
		await client.send_poi(car_id, poi_lat, poi_long, poi_name)
		# Close the session
		await client.close()
		return

	if not do_engine and not do_doors:
		await output_car_data(car_id)
	else:
		# run the engine task
		if do_engine:
			await control_engine(car_id, do_engine)
	
		# run the door lock task
		if do_doors:
			await control_locks(car_id, do_engine)

	# Close the session
	await client.close()

# Initialize API client (MNAO = North America)
client = pymazda.Client(email, password, "MNAO")

# Run the job
loop = asyncio.get_event_loop()
loop.run_until_complete(main_job())

