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
    
    def save2path(self, df: pd.DataFrame, researcher_initials: str, participant_id: str):
        current_date = datetime.now().strftime("%Y_%m_%d")
        raw_excel_file_name = f"preprocessed_data_{participant_id}_{researcher_initials}_{current_date}.csv"
        script_dir = Path(__file__).resolve().parent.parent
        data_folder = script_dir.parent / "data" / "raw"
        raw_excel_path = data_folder / raw_excel_file_name
        if not data_folder.exists():
            data_folder.mkdir(parents=True)
        df.to_csv(raw_excel_path)
        return raw_excel_path


def main(data_file: Path, sampling_rate: int, researcher_initials: str, participant_id: str):
    print("Making dataset...")
    logger = logging.getLogger(__name__)
    logger.info('making final data set from .mat raw data')

    data_prep = DataPreparation(data_file, sampling_rate)
    data, labels, units = data_prep.load_data()

    if data is not None:
        df = data_prep.create_dataframe(data, labels, units)
        raw_excel_path = data_prep.save2path(df, researcher_initials, participant_id)
        print(f"Dataset created and saved in {raw_excel_path}")

    return df

if __name__ == '__main__':
    main()