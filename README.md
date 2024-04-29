# synthpop

The following steps to be followed to generate the synthetic population.

1. First, install the synthpoppp library from github

    Recommended: Install a virtual environment:

        python3 -m venv venv_for_synthpop
	    source venv_for_synthpop/bin/activate

 Use the following command to install the synthpopp library.
    
        pip3 install git+https://github.com/bhaveshneekhra/synthpoppp/


2. The following command is used to generate the synthpop for the city (the source files should be provided- see the next point for the description):

        python3 generate.py  

    The OPTIONAL arguments are defined as follows:

        --n_proc: Number of worker processes in the Pool to leverage multiple processors on a given machine (default=1)
        --subset: Whether to subset for the district/city in the source file (default=False)
        --debug: Prints detailed messages if True, default: False
        --overwrite: Overwrites the earlier synthetic population (default=False)

3. The source files (description for each file is inline) should be provided in the following directory structure:

        district_level_source_files
            |
            ---<STATE NAME> (Name of the state for which the synthetic population is to be generated)
                    |
                    ---<City/District Name> (Name of the district/city for which the synthetic population is to be generated
                    |
                    ---admin_unit_wise_pop.csv  (This file contains administrative units under the city/district, its longitude and latitude and population)
                    ---admin_units.geojson (This file contains the geogprahic features for the city/district with its administrative units)
                    ---household_marg.csv (This file has the household sizes and the number of household of that size in the city/district. Curated from Census data)
                    ---person_marg.csv (This file contains the total population, distribution acorss sexes, age groups, religion and caste of the city/district. Curated from Census data)
                    
        nation_level_source_files (these are compressed files to save space, uncompress them before running the code)
            |
            ---survey data files for the state (There are two files from IHDS-II survey (https://www.icpsr.umich.edu/web/DSDR/studies/36151/summary). 
                (1) 36151-0001-Data.tsv: Survey of Individuals)
                (2) 36151-0002-Data.tsv: Survey of Households)
            ---population density file for the country 
                    GPW projection for population density for India. (Source: https://data.worldpop.org/GIS/Population_Density/Global_2000_2020_1km/2020/IND/ind_pd_2020_1km_ASCII_XYZ.zip)

4. The base population is saved as synthetic.csv inside the directory structure:
            
            district_level_source_files --> <STATE NAME> --> <City/District Name>
