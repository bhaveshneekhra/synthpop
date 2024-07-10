import numpy as np
import pandas as pd

from synthpoppp.base_population import IPU
from synthpoppp.helper_constants import *
from synthpoppp.geographical_distributions import HLatHlongAgeAddition, JobsPlacesAddition

import argparse
import datetime
import traceback

import os
import json
import gc

from multiprocessing import Pool

from expand_base_population import add_features

parser = argparse.ArgumentParser()


# The bool() function is not recommended as a type converter. All it does is convert empty strings to False and non-empty strings to True. This is usually not what is desired.

parser.add_argument('--mean_wkplace_size', default=100)
parser.add_argument('--n_proc', default=1)
parser.add_argument('--debug', default=False)
parser.add_argument('--subset', default="")
parser.add_argument('--overwrite', default=True)

arguments = parser.parse_args()

mean_wkplace_size = int(arguments.mean_wkplace_size)
n_proc = int(arguments.n_proc)
DEBUG = arguments.debug=="True" or arguments.debug=="true"
overwrite = arguments.overwrite=="True" or arguments.overwrite=="true"
subset = arguments.subset.split(",")
subsetting = subset[0]!=""

if True:
	print("The arguments supplied: n_proc=%d, debug=%s, overwrite=%s, subset=%s" %(n_proc, DEBUG, overwrite, subset))

start = datetime.datetime.now()

nation_level_source_files_dir = "nation_level_source_files"
district_level_source_files_dir = "district_level_source_files"

ihds_individuals_filename = os.path.join(nation_level_source_files_dir, "36151-0001-Data.tsv")
ihds_household_filename = os.path.join(nation_level_source_files_dir, "36151-0002-Data.tsv")
population_density_filename = os.path.join(nation_level_source_files_dir, "ind_pd_2020_1km_ASCII_XYZ.csv")

ihds_individuals_data = pd.read_csv(ihds_individuals_filename, sep='\t')
ihds_households_data = pd.read_csv(ihds_household_filename, sep='\t')

india_config = json.loads(open("config.json").read())

source_file_state_names = os.listdir("district_level_source_files")

if(not subsetting):
	subset = source_file_state_names

if(DEBUG):
	if subset =="":
		print("Synthpop generated using the state data filtered from IHDS-II survey.")
	else:
		print("Synthpop generated from subset(s) %s filtered from IHDS-II survey." % subset)

def generate_base_synthpop(ihds_state_id, district_source_files_path):
	households_marginal_filename = os.path.join(district_source_files_path, "household_marg.csv")
	individuals_marginal_filename = os.path.join(district_source_files_path, "person_marg.csv")
	admin_units_geojson_filename = os.path.join(district_source_files_path, "admin_units.geojson")
	admin_units_population_filename = os.path.join(district_source_files_path, "admin_unit_wise_pop.csv")
	
	
	if(DEBUG):
		print("Source file names:")
		print(
			households_marginal_filename,
			individuals_marginal_filename,
			admin_units_geojson_filename,
			admin_units_population_filename,
			sep="\n"
		) 
	filtered_ihds_individuals_data = ihds_individuals_data.loc[ihds_individuals_data.STATEID==ihds_state_id]			

	filtered_ihds_households_data = ihds_households_data.loc[ihds_households_data.STATEID==ihds_state_id] 

	ipu_object = IPU()
	synthetic_households, synthetic_individuals, synthetic_stats = ipu_object.generate_data(filtered_ihds_individuals_data, filtered_ihds_households_data, households_marginal_filename, individuals_marginal_filename) 
	
	if(DEBUG):
		print("Households generated:")
		print(synthetic_households)
		print("Individuals generated:")
		print(synthetic_individuals)
		


	hlat_hlong_age_object = HLatHlongAgeAddition(admin_units_geojson_filename, admin_units_population_filename, population_density_filename)
	base_synthetic_population = hlat_hlong_age_object.perform_transforms(synthetic_individuals, synthetic_households)

	if DEBUG:
		print("Synthetic population with geographic information added:")
		print(base_synthetic_population)
	
	if DEBUG:
		print(POSSIBLE_JOB_LABELS)
	
	tot_pop = len(base_synthetic_population)
	num_wkplaces = np.int64(tot_pop / mean_wkplace_size) # Mean workplace size default value is 100. 
	num_public_places = np.int64(num_wkplaces / 10) # This is just a heuristic now. Based on better estimates, we can update this.

	if DEBUG:
		print("Total population generated: %d" % tot_pop)
		print("Number of work places to be assigned: %d" % num_wkplaces)
		print("Number of public places to be assigned: %d" % num_public_places)
		
	jobs_places_object = JobsPlacesAddition(POSSIBLE_JOB_LABELS, admin_units_geojson_filename, num_wkplaces, num_public_places, population_density_filename, 'default', 'default', 'default')
	base_synthetic_population = jobs_places_object.perform_transforms(base_synthetic_population) 

	if DEBUG:
		print("Synthetic population with job labels added:")
		print(base_synthetic_population)

	return base_synthetic_population

def generate_and_save_data(ihds_state_id, state_name, district_name, district_source_files_path):
	try:
		synthetic_population_output_filename = os.path.join(district_source_files_path, "synthetic.csv")


		synthetic_population = generate_base_synthpop(ihds_state_id, district_source_files_path)

		#  Expand base population
		add_features(synthetic_population, state_name, district_name, district_source_files_path)
		#  Asign workplace
		
		print("\n\n****************************************************************")
		print("\n\nThe final synthetic population for %s is saved in %s" % (district_name, synthetic_population_output_filename))
		print("\n\n****************************************************************")

		synthetic_population.to_csv(synthetic_population_output_filename, index=False)

		del(synthetic_population)

		gc.collect()
		return True

	except Exception as e:
		print(f"FatalException | STATE_ID: {ihds_state_id} | DISTRICT: {district_source_files_path} | ErrorMessage: {repr(e)}")
		print(traceback.format_exc())
		return False


args_to_pass = []

skip = [".DS_Store"]

for source_file_state_name in source_file_state_names:
	if source_file_state_name in skip:
		continue
	if source_file_state_name in subset:
		ihds_state_name = india_config['source_files_to_ihds_state_name_map'][source_file_state_name]
		ihds_state_id = IHDS_II_STATE_NAME_TO_ID[ihds_state_name]
		state_source_files_dir = os.path.join(district_level_source_files_dir, source_file_state_name)
		districts_in_state = os.listdir(state_source_files_dir)
		for district_name in districts_in_state:
			if district_name in skip:
				continue
			district_source_files_path = os.path.join(state_source_files_dir, district_name)
			synthetic_population_output_filename = os.path.join(district_source_files_path, "synthetic.csv")
			if not overwrite:
				if not os.path.exists(synthetic_population_output_filename):
					args_to_pass.append((ihds_state_id, source_file_state_name, district_name, district_source_files_path)) 
				else: 
					print("\n\n****************************************************************")
					print("\n\nSkipping generating synthetic population as it already exists for %s." % district_name)
					print("\n\n****************************************************************")
			else:
				args_to_pass.append((ihds_state_id, source_file_state_name, district_name, district_source_files_path))

args_to_pass = sorted(args_to_pass, key=lambda x : x[1])

if DEBUG and len(args_to_pass)!=0:
	print("Synthetic population to be generated: %s" % args_to_pass)

if __name__ == '__main__':
	multiprocess_pool = Pool(n_proc)

	output = multiprocess_pool.starmap(generate_and_save_data, args_to_pass)
	multiprocess_pool.terminate()

							
	end = datetime.datetime.now()

	failed_districts = [x[0] for x in zip(args_to_pass, output) if not x[1]]
	if len(failed_districts) >0:
		print("\n\n****************************************************************")
		print("\n\nGenerating synthetic population failed for districts:")
		for failed_district in failed_districts:
			print(failed_districts)
		print("****************************************************************\n\n")
	if(DEBUG):
		print("Started At :", start, "\nEnded At :", end, "\nWall Time :", end-start)
