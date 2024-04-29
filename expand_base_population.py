import pandas as pd
import numpy as np
import geopandas as gpd
import os


def add_features(base_pop_df, state_name, district_name, district_source_files_path, agentid_offset=521000000000):
    # agentid_offset: To guarantee unique AgentIDs in a nationwide synthetic population, we add an offset to all generated AgentIDs.   
    # This offset is a 13 digit number with format: SS DD AAAAAAAAA
    # SS: Two digit state id from Census. Leading zeros are ignored. (For Maharashtra: 5)
    # DD: Two digit district id from Census. (For Pune: 21)
    # AAAAAAAAA: Unique nine digit AgentID generated in base synthetic population
    # This assumes a maximum number of 1 billion (10^9) unique agents per district.

    # Delete columns not needed for BharatSim  
    #     cat_id
    #     geog
    #     mem_id
    #     sample_geog
    #     serialno
    #     WorksAtSameCategory
    #     district

    try:
        base_pop_df.drop(columns=['district', 'cat_id','geog', 'mem_id', 'sample_geog', 'serialno', 'WorksAtSameCategory'], inplace=True)
    except:
        pass

    base_pop_df["District"] = district_name
    base_pop_df['StateLabel'] = state_name

    base_pop_df['AgentID'] = base_pop_df.index + agentid_offset 


    # Add Adherence to intervention based on age
    base_pop_df['Adherence_to_Intervention'] = 0.0

    #     Age-group	Adherence_to_Intervention
    #         0-9	    1.0
    #         10-14	    0.8
    #         15-19	    0.4
    #         20-24	    0.3
    #         25-29	    0.2
    #         30-34	    0.1
    #         35-40	    0.0
    #         41-59	    0.9
    #         60-99	    1.0

    base_pop_df.loc[(base_pop_df['Age'] >=0)  & (base_pop_df['Age'] <=9), 'Adherence_to_Intervention'] = 1.0
    base_pop_df.loc[(base_pop_df['Age'] >=10)  & (base_pop_df['Age'] <=14), 'Adherence_to_Intervention'] = 0.8
    base_pop_df.loc[(base_pop_df['Age'] >=15)  & (base_pop_df['Age'] <=19), 'Adherence_to_Intervention'] = 0.4
    base_pop_df.loc[(base_pop_df['Age'] >=20)  & (base_pop_df['Age'] <=24), 'Adherence_to_Intervention'] = 0.3
    base_pop_df.loc[(base_pop_df['Age'] >=25)  & (base_pop_df['Age'] <=29), 'Adherence_to_Intervention'] = 0.2
    base_pop_df.loc[(base_pop_df['Age'] >=30)  & (base_pop_df['Age'] <=34), 'Adherence_to_Intervention'] = 0.1
    base_pop_df.loc[(base_pop_df['Age'] >=35)  & (base_pop_df['Age'] <=40), 'Adherence_to_Intervention'] = 0.0
    base_pop_df.loc[(base_pop_df['Age'] >=41)  & (base_pop_df['Age'] <=59), 'Adherence_to_Intervention'] = 0.9
    base_pop_df.loc[(base_pop_df['Age'] >=60)  & (base_pop_df['Age'] <=99), 'Adherence_to_Intervention'] = 1.0

    # Rename columns

    base_pop_df.rename(columns = {'JobType':'JobLabel','household_id': 'HHID'}, inplace=True)
    base_pop_df.rename(columns = {'WorkplaceID':'WorkPlaceID'}, inplace = True)
    # base_pop_df.rename(columns = {'SchoolID': 'school_id','School_Lat':'school_lat','School_Lon':'school_long'}, inplace=True)
    base_pop_df.rename(columns = {'PublicPlaceID': 'public_place_id', 'PublicPlaceLat': 'public_place_lat','PublicPlaceLong':'public_place_long'}, inplace=True)
    base_pop_df.rename(columns = {'AdminUnitName':'AdminUnit_Name', 'AdminUnitLatitude' : 'AdminUnit_Lat', 'AdminUnitLongitude' : 'AdminUnit_Lon'}, inplace = True)
    base_pop_df.rename(columns = {'Adherence_to_Intervention':'AdherenceToIntervention'}, inplace = True)
    base_pop_df.rename(columns = {'school_id' : 'SchoolID', 'school_lat' : 'School_Lat', 'school_long' :'School_Lon'}, inplace=True)
    base_pop_df.rename(columns = {'public_place_id': 'PublicPlaceID', 'public_place_lat': 'PublicPlace_Lat','public_place_long':'PublicPlace_Lon'}, inplace=True)

    # Modify Columns

    base_pop_df['WorkPlaceID'] = base_pop_df['WorkPlaceID'].fillna(0)
    base_pop_df['SchoolID'] = base_pop_df['SchoolID'].fillna(0)
    base_pop_df[['WorkPlaceID']] = base_pop_df[['WorkPlaceID']].astype(pd.Int64Dtype())
    base_pop_df[['SchoolID']] = base_pop_df[['SchoolID']].astype(pd.Int64Dtype())

    # If WorkPlaceID=0, and SchoolID != 0, then assign JobLabel: Student

    base_pop_df['JobLabel'] = np.where((base_pop_df['WorkPlaceID'] == 0) & (base_pop_df['SchoolID'] != 0) , "Student", base_pop_df['JobLabel'])

  # For Age=0, 1, 2, 3 JobLabel=Homebound

    base_pop_df['JobLabel'] = np.where((base_pop_df['Age'] == 0), "Homebound", base_pop_df['JobLabel'])
    base_pop_df['JobLabel'] = np.where((base_pop_df['Age'] == 1), "Homebound", base_pop_df['JobLabel'])
    base_pop_df['JobLabel'] = np.where((base_pop_df['Age'] == 2), "Homebound", base_pop_df['JobLabel'])
    base_pop_df['JobLabel'] = np.where((base_pop_df['Age'] == 3), "Homebound", base_pop_df['JobLabel'])

    # For homebound people: SchoolID=0, School_Lat=nan, School_Lon=nan, WorkPlaceID=0, W_Lat, W_Lon, EssentialWorker=0

    base_pop_df.loc[base_pop_df.JobLabel == "Homebound", ['WorkPlaceID', 'W_Lat', 'W_Lon', 'SchoolID', 'School_Lat', 'School_Lon' ]] = [0, np.nan, np.nan, 0, np.nan, np.nan]

    # Asisgn EssentialWorker based on the JobLabel 

    essential_list = ['Police', 'Sweepers', 'Sales, shop', 'Shopkeepers', 'Boilermen', 
                      'Nursing', 'Journalists', 'Electrical', 'Food', 'Physicians', 
                      'Mail distributors', 'Loaders', 'Village officials', 'Govt officials', 'Telephone op']
    non_essential_list = list(set(base_pop_df['JobLabel'].unique()) - set(essential_list)) 

    base_pop_df['EssentialWorker'] = np.where(base_pop_df['JobLabel'].isin(essential_list) & base_pop_df['Age'] > 16, True, False)

    UsesPrivateTransport = ['Police','Govt Officials','Teachers','Engineers','Managerial nec',
                          'Production nec','Textile','Professional nec','Journalists','Economists',
                          'Jewellery','Shopkeepers','Physicians','Computing op','Mgr manf','Technical sales']
    
    base_pop_df['UsesPublicTransport'] = np.where(base_pop_df['JobLabel'].isin(UsesPrivateTransport), False, True)

    # Add ward names to Schools and Workplaces

    district_geojson_fname = os.path.join(district_source_files_path, "admin_units.geojson")
    gdf = gpd.read_file(district_geojson_fname)

    points_gdf = gpd.GeoDataFrame(base_pop_df, geometry=gpd.points_from_xy(base_pop_df.W_Lon, base_pop_df.W_Lat))
    joined = gpd.sjoin(points_gdf, gdf, how='inner', op='within')

    base_pop_df['WorkPlace_AdminUnit'] = joined['name']

    points_gdf = gpd.GeoDataFrame(base_pop_df, geometry=gpd.points_from_xy(base_pop_df.School_Lon, base_pop_df.School_Lat))
    joined = gpd.sjoin(points_gdf, gdf, how='inner', op='within')

    base_pop_df['School_AdminUnit'] = joined['name']

    # Save the df into the specified format

    base_pop_df = base_pop_df[['AgentID', 'SexLabel', 'Age', 'Religion', 'Caste', 
    'StateLabel', 'District',
    'JobLabel', 'EssentialWorker',
    'AdminUnit_Name', 'AdminUnit_Lat', 'AdminUnit_Lon', 
    'HHID', 'H_Lat', 'H_Lon',
    'AdherenceToIntervention', 'UsesPublicTransport',       
    'WorkPlaceID', 'W_Lat', 'W_Lon', 'WorkPlace_AdminUnit',
    'SchoolID', 'School_Lat', 'School_Lon', 'School_AdminUnit',
    'PublicPlaceID', 'PublicPlace_Lat', 'PublicPlace_Lon'     
            ]]

    return base_pop_df