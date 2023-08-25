import logging
from pathlib import Path
from scipy.io import loadmat
import numpy as np
import pandas as pd
from dotenv import find_dotenv, load_dotenv
import os
from datetime import datetime

# if acq file -> load acq file -> data, sampling_rate = nk.read_acqknowledge('file.acq') 
class DataPreparation:
    def __init__(self, filepath: Path, sampling_rate: int):
        self.filepath = filepath
        self.sampling_rate = sampling_rate

    def load_data(self) -> tuple:
        try:
            data_dict = loadmat(self.filepath)
            return data_dict['data'], data_dict['labels'].flatten(), data_dict['units'].flatten()
        except (FileNotFoundError, IOError) as e:
            logging.error(f"Error loading mat file: {e}")
            return None, None, None

    def create_dataframe(self, data: np.array, labels: np.array, units: np.array) -> pd.DataFrame:
        labels_units = [f'{label} ({unit})' for label, unit in zip(labels, units)]
        return pd.DataFrame(data, columns=labels_units)

''' if click is used, then the following code is used to run the script from the command line
#@click.command()
#@click.argument('data_file', type=click.Path(exists=True))
#@click.argument('sampling_rate', type=int)
#@click.argument('excel_path', type=click.Path())
'''

def main(data_file: Path, sampling_rate: int, researcher_initials: str):
    print("Making dataset...")
    logger = logging.getLogger(__name__)
    logger.info('making final data set from .mat raw data')

    data_prep = DataPreparation(data_file, sampling_rate)
    data, labels, units = data_prep.load_data()

    if data is not None:
        df = data_prep.create_dataframe(data, labels, units)
        # Save the raw dataframe
        # Define path to save processed data
        current_date = datetime.now().strftime("%Y_%m_%d")
        raw_excel_file_name = f"preprocessed_data_{researcher_initials}_{current_date}.csv"
        raw_excel_path = os.path.join(os.path.dirname(__file__), "data", "raw", raw_excel_file_name)
        df.to_csv(raw_excel_path)

    print(f"Dataset created and saved in {raw_data_path}!")
    return df

if __name__ == '__main__':
    main()