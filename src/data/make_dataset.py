# -*- coding: utf-8 -*-
#import click
import logging
from pathlib import Path
from scipy.io import loadmat
import numpy as np
import pandas as pd
from dotenv import find_dotenv, load_dotenv

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

def main(data_file: Path, sampling_rate: int, excel_path: Path):
    logger = logging.getLogger(__name__)
    logger.info('making final data set from .mat raw data')

    data_prep = DataPreparation(data_file, sampling_rate)
    data, labels, units = data_prep.load_data()

    if data is not None:
        df = data_prep.create_dataframe(data, labels, units)
        # You may want to do something with df and excel_path here

    print("Dataset created!")  # Moved inside the main function
    return df

if __name__ == '__main__':
    main()

    

    

