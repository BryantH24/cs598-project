#!/usr/bin/env python3
"""
Pipeline Runner Script

This script executes all the data processing notebooks or the specified steps in the pipeline.

Arguments: 
--step: Run only the specified step numbers (comma-separated, e.g., 1,3,5)
--dataSubsetRows: Number of rows to keep from CFB data (for testing with smaller datasets)
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

PIPELINE_STEPS = [
    {
        'number': 1,
        'name': 'Fetch Data',
        'notebooks': ['1_fetch_data/cfb_data_pipeline.ipynb', '1_fetch_data/school_locations_pipeline.ipynb'],
        'description': 'Download college football data and school locations'
    },
    {
        'number': 2,
        'name': 'Validate Data',
        'notebook': '2_validate_data/cfb_data_validator.ipynb',
        'description': 'Validate CFB dataset using LLM sampling'
    },
    {
        'number': 3,
        'name': 'Preprocess School Matching',
        'notebook': '3_preprocess_school_matching/school_location_matcher.ipynb',
        'description': 'Match school names between datasets'
    },
    {
        'number': 4,
        'name': 'Fetch Venue Locations',
        'notebook': '4_fetch_venue_locations/fetch_venue_locations.ipynb',
        'description': 'Get venue location data from CFB API'
    },
    {
        'number': 5,
        'name': 'Combine CFB and Locations',
        'notebook': '5_combine_cfb_and_locations/combine_cfb_and_locations.ipynb',
        'description': 'Combine game data with location information'
    },
    {
        'number': 6,
        'name': 'Enrich Weather Data',
        'notebook': '6_enrich_weather_data/enrich_game_weather_data.ipynb',
        'description': 'Add weather data to game records'
    },
    {
        'number': 7,
        'name': 'Enrich School Weather Data',
        'notebook': '7_fetch_school_weather_data/enrich_school_weather_data.ipynb',
        'description': 'Add weather data to school records'
    },
        'number': 8,
        'name': 'Generate Codebooks',
        'notebook': '8_generate_codebooks/generate_codebook.ipynb',
        'description': 'Generate codebooks for all CSV files in the repository'
    }
]

def run_notebook(notebook_path, step_info, data_subset_rows=None):
    """
    Execute a notebook as a script.
    """

    print("Running notebook: " + notebook_path + " (Step " + str(step_info['number']) + " - " + step_info['name'] + ")")
    try:
        src_dir = Path(__file__).parent
        os.chdir(src_dir)

        env = os.environ.copy()
        if data_subset_rows is not None:
            env['DATA_SUBSET_ROWS'] = str(data_subset_rows)

        cmd = [
            sys.executable, '-m', 'nbconvert',
            '--to', 'notebook',
            '--execute',
            '--inplace',
            '--ExecutePreprocessor.timeout=-1',
            notebook_path
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=None,
            env=env
        )

        if result.returncode == 0:
            return True
        else:
            print("Error: Notebook " + notebook_path + " (Step " + str(step_info['number']) + ") failed with return code " + str(result.returncode))
            print("STDOUT: " + result.stdout)
            print("STDERR: " + result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("Error: Notebook " + notebook_path + " (Step " + str(step_info['number']) + ") timed out")
        return False
    except FileNotFoundError:
        print("Error: Notebook file not found: " + notebook_path)
        return False
    except Exception as e:
        print("Error: Unexpected error running notebook " + notebook_path + " (Step " + str(step_info['number']) + "): " + str(e))
        return False

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the college football data processing pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py                                      # Run all steps
  python run_pipeline.py --step 3                             # Run only step 3
  python run_pipeline.py --step 1,3,5                         # Run steps 1, 3, and 5
  python run_pipeline.py --dataSubsetRows 10                # Run all steps with only 10 rows of data
  python run_pipeline.py --step 1 --dataSubsetRows 5        # Run step 1 with only 5 rows
        """
    )

    parser.add_argument(
        '--step',
        type=lambda x: [int(i) for i in x.split(',')],
        help='Run only the specified step numbers (comma-separated, e.g., 1,3,5)'
    )

    parser.add_argument(
        '--dataSubsetRows',
        type=int,
        help='Number of rows to keep from CFB data (for testing with smaller datasets)'
    )

    return parser.parse_args()

def get_steps_to_run(args):
    if args.step:
        return [step for step in PIPELINE_STEPS if step['number'] in args.step]
    return PIPELINE_STEPS

def main():
    """Main pipeline execution function."""
    args = parse_arguments()

    steps_to_run = get_steps_to_run(args)
    total_steps = len(steps_to_run)

    start_time = datetime.now()
    success_count = 0

    for step in steps_to_run:
        step_number = step['number']

        notebooks = step.get('notebooks', [step.get('notebook')])
        if notebooks is None:
            print("Error: Step " + str(step_number) + " has no notebook(s) defined")
            return False

        step_success = True
        for notebook_path in notebooks:
            src_dir = Path(__file__).parent
            full_notebook_path = src_dir / notebook_path
            if not full_notebook_path.exists():
                print("Error: Notebook not found: " + str(full_notebook_path))
                step_success = False
                break

            if not run_notebook(notebook_path, step, args.dataSubsetRows):
                step_success = False
                break

        if step_success:
            success_count += 1
        else:
            print("Error: Pipeline failed at Step " + str(step_number))
            break

    end_time = datetime.now()
    duration = end_time - start_time

    if success_count == total_steps:
        if total_steps == len(PIPELINE_STEPS):
            print("FULL PIPELINE COMPLETED SUCCESSFULLY")
        else:
            print("SELECTED STEPS COMPLETED SUCCESSFULLY")
    else:
        print("EXECUTION COMPLETED WITH ERRORS - " + str(success_count) + "/" + str(total_steps) + " steps completed")

    print("Total execution time: " + str(duration))

    return success_count == total_steps

if __name__ == "__main__":
    main()
