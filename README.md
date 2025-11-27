# College Football Dataset with Location and Weather

## Overview
This repository contains a college football dataset covering all NCAA FBS games from 2002 to 2024 from https://www.kaggle.com/datasets/cviaxmiwnptr/college-football-team-stats-2002-to-january-2024. This data is enriched by matching each school with it's official school name from https://catalog.data.gov/dataset/postsecondary-school-locations-2020-21-c5470 for location data, and https://collegefootballdata.com/ for neutral game data. Weather data for the games as well as the average weather for the school's location is sourced from https://open-meteo.com. 

## Organization
The raw datasets from Kaggle and catalog.data.gov are stored under `/college_football_data` and `/postsecondary_school_locations` respectively. Intermediate files generated during the execution of scripts are stored in `/intermediate_files`. 

The scripts needed to process, enrich, and analyze the data are stored under `/src`. Each subfolder in the source folder begins with a number to indicate the ordering for execution, but each step can also be executed independently as long as it's prerequisite files are available. 

The `utils` folder contains utility modules needed to run the script. `llm_utils.py` stores the Google Gemini API key and provides a reusable request function. `cfb_api_utils.py` stores the collegefootballdata.com API key. `get_file_paths.py` provides a utility function for getting the data file names from the CFB and NCES data.

Subfolder steps: 
- `1_fetch_data`: retrieves the raw CSV files from Kaggle and catalog.data.gov and stores them into the repository. 
- `2_validate_data`: uses Google Gemini LLM to validate data from the college football repository and stores validation results in `/intermediate_files/validation_results`. This step is optional
- `3_preprocess_school_matching`: uses Google Gemini LLM to match school names from the Kaggle dataset with the catalog.data.gov dataset. It creates a file to store this mapping, along with the corresponding school's location (latitude and longitude) from the catalog.data.gov data set.
- `4_fetch_venue_locations`: uses collegefootballdata.com to retrieve game locations per venue, used for neutral site game. 
- `5_combine_cfb_and_locations`: processes the enrichment of home, away, and actual locations for game data. It uses both the location mapping from step 3 as well as the venue location from step 4 to handle neutral site games. 
- `6_enrich_games_weather_data`: uses open-meteo.com api to add weather data to the dataset. The game weather data script adds weather data for each specific game. 
- `7_fetch_school_weather_data`: The school weather data script determines the average weather for a specific location during football season and creates a new school to weather data set. 

## Steps to Run Data Pipeline

### Add API Keys
1. Populate `cfb_api_utils.py` with API key from collegefootballdata.com (needed for steps 4, 5)
2. Populate `llm_utils.py` with API key from Google Gemini (needed for steps 2, 3)

### Prepare Python Environment
Prerequisite requirements: Python 3.13 installed on machine
1. Create a Virtual Environment: `python3 -m venv venv`
2. Activate it: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the pipeline, example command: `venv/bin/python3 src/run_pipeline.py --step 1,4,5,6 --dataSubsetRows 5`
* Notes for reproducing: skip steps 2 and 3 since they use Gemini LLM, skip step 7 since it takes a long time and can hit open-meteo daily API limit. 


## Known Issues
- Steps requiring Google Gemini LLM (2, 3) may not produce exact results on multiple runs. 
- open-meteo.org API free tier has strict quota limits that the current script may hit during step 6. This step can be rerun and data will be aggregated across multiple runs.  