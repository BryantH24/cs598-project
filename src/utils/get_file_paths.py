import os

def get_cfb_data_path():
    college_football_data_dir = "../../college_football_data"
    csv_files = [f for f in os.listdir(college_football_data_dir) if f.endswith('.csv')]

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {college_football_data_dir}")
    elif len(csv_files) > 1:
        print(f"Warning: Multiple CSV files found: {csv_files}. Using the first one: {csv_files[0]}")

    CFB_DATA_PATH = os.path.join(college_football_data_dir, csv_files[0])
    return CFB_DATA_PATH

def get_nces_data_path():
    nces_data_dir = "../../postsecondary_school_locations"
    csv_files = [f for f in os.listdir(nces_data_dir) if f.endswith('.csv')]

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {nces_data_dir}")
    elif len(csv_files) > 1:
        print(f"Warning: Multiple CSV files found: {csv_files}. Using the first one: {csv_files[0]}")

    NCES_DATA_PATH = os.path.join(nces_data_dir, csv_files[0])
    return NCES_DATA_PATH