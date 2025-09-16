# 🏙️ Synthetic Population Generator for Indian Districts

This project allows you to generate **synthetic populations** for cities and districts in India. Using Census marginals, IHDS-II survey data, and geographic boundaries, it creates realistic populations suitable for modeling, simulation, or demographic analysis.  

This synthetic population generator builds on our previous research:

- **Bhavesh Neekhra et al. (2023)** – *Synthpop++: A Hybrid Framework for Generating A Country-scale Synthetic Population*. [arXiv:2304.12284](https://arxiv.org/abs/2304.12284)

This paper introduces methods for creating realistic, high-fidelity synthetic populations using survey and census data, which form the foundation of this tool.

---

## ✨ Features
- 🏘️ Generates district-level synthetic populations.
- 👨‍👩‍👧‍👦 Leverages household and individual survey data for realism.
- 🌍 Uses geospatial boundaries to assign populations to administrative units.
- ⚡ Supports multi-processing for faster generation.

---

## 🚀 Quick Start

### 1️⃣ Clone the repository
```bash
💻 git clone https://github.com/bhaveshneekhra/synthpop.git
cd synthpop
```
### 2️⃣ Set up a virtual environment (recommended)
```bash
python3 -m venv venv_for_synthpop
source venv_for_synthpop/bin/activate
```
### 3️⃣ Install dependencies
```bash
🛠️  pip install -r requirements.txt 
```

⚠️ Note: Make sure to unzip all files in nation_level_source_files/ before running. You should have the following directory structure. 

📁 Directory Structure
        
        district_level_source_files/
        |
        |--- <STATE NAME>/
            |
            |--- <CITY_OR_DISTRICT_NAME>/
                    |--- admin_unit_wise_pop.csv   # Admin units with population, lat, long
                    |--- admin_units.geojson       # Geo boundaries
                    |--- household_marg.csv        # Household size distribution
                    |--- person_marg.csv           # Population by sex, age, religion, caste

        nation_level_source_files/
        |
        |--- 36151-0001-Data.tsv       # IHDS-II survey of individuals
        |--- 36151-0002-Data.tsv       # IHDS-II survey of households
        |--- ind_pd_2020_1km_ASCII_XYZ.csv  # Population density map for India

### 4️⃣ Running the Generator

The main script is generate.py. Run it with:
```bash
python3 generate.py
```

    ⚙️ Optional arguments
        •	--n_proc: Number of processes for parallel computation (default: 1)
        •	--subset: Only generate for the target city/district (default: False)
        •	--debug: Print detailed logs (default: False)
        •	--overwrite: Overwrite existing synthetic population (default: False)


💾 Output

The generated synthetic population is saved as:
```bash
district_level_source_files/<STATE NAME>/<CITY_OR_DISTRICT_NAME>/synthetic.csv
```

Each row represents an individual with demographic attributes and assigned household.

    📚 Data Sources
        •	📝 IHDS-II Survey (2011–12)
        •	🏛️ Census of India (2011)
        •	🌐 GPW Population Density (2020)


🔄 Data Flow Diagram

    nation_level_source_files/       district_level_source_files/
    -------------------------------- ------------------------------
    | 36151-0001-Data.tsv  |        | admin_unit_wise_pop.csv       |
    | 36151-0002-Data.tsv  |        | admin_units.geojson           |
    | ind_pd_2020_1km_ASCII_XYZ.zip | household_marg.csv            |
                                    | person_marg.csv               |
    -------------------------------- ------------------------------

            Survey & Census Data
                        │
                        ▼
            Population Assignment Engine
                        │
                        ▼
            Household & Individual Synthesis
                        │
                        ▼
    district_level_source_files/<STATE>/<CITY>/synthetic.csv


⚖️ License

MIT License. See LICENSE for details.