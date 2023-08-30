import neurokit2 as nk
import pandas as pd
import os
from datetime import datetime
from pathlib import Path

class FeatureBuilder:
    def __init__(self, 
                 df: pd.DataFrame, 
                 sampling_rate: int, 
                 column_labels: dict = None):
        self.df = df
        self.sampling_rate = sampling_rate
        self.column_labels = column_labels

    def _process(self, process_func, column_label):
        processed_signals, _ = process_func(self.df[column_label], self.sampling_rate)
        return processed_signals

    def _process_slider(self):
        column_label = self.column_labels['slider']
        if column_label in self.df.columns:
            slider_scores = self.df[column_label]
            filtered_signal = nk.signal_filter(slider_scores, 
                                               method="savgol", 
                                               sampling_rate=self.sampling_rate, 
                                               lowcut=0.1, 
                                               highcut=None)
            return pd.DataFrame({'slider': filtered_signal})
        return None

    def process_signals(self):
        processed_dataframes = {}
        for signal_type, process_func in zip(['ecg', 'rsp', 'eda', 'ppg'], 
                                             [nk.ecg_process, nk.rsp_process, nk.eda_process, nk.ppg_process]):
            processed_dataframes[signal_type] = self._process(process_func, self.column_labels[signal_type])
        
        processed_dataframes['slider'] = self._process_slider()

        events = self._create_events()

        return processed_dataframes, events

    def _create_events(self):
        event_labels = ["Absorptive", "1stSilence", "Self-Chosen Absorptive", "2ndSilence", "Self-Chosen Non-absorptive", "3rdSilence"]
        event_labels_unique = [f"{label}_{i+1}" for i, label in enumerate(event_labels)]
        event_onsets_seconds = [0, 420, 600, 1020, 1200, 1620]
        event_onsets_indices = [int(i * self.sampling_rate) for i in event_onsets_seconds]
        return nk.events_create(event_onsets=event_onsets_indices, event_labels=event_labels_unique)
 
    def save2path(self, df: pd.DataFrame, researcher_initials: str, participant_id: str, feature_type: str):
        current_date = datetime.now().strftime("%Y_%m_%d")
        
        # Create a folder name with initials, id and date
        folder_name = f"{researcher_initials}_{participant_id}_{current_date}"
        
        script_dir = Path(__file__).resolve().parent.parent
        data_folder = script_dir.parent / "data" / "interim" / folder_name
        
        # Create a new folder if it does not exist
        if not data_folder.exists():
            data_folder.mkdir(parents=True)
        
        # Generate Excel file name based on feature_type
        excel_file_name = f"intermediate_data_{feature_type}.csv"
        
        # Create complete Excel path
        excel_path = data_folder / excel_file_name
        
        # Save the DataFrame to CSV
        df.to_csv(excel_path)
        
        return excel_path

def main(df: pd.DataFrame, sampling_rate: int, researcher_initials: str, participant_id: str):
    print("Building features...")
    
    column_labels = {
            "eda": "EDA100C (microsiemens)",
            "rsp": "RSP100C (Volts)",
            "ecg": "ECG100C (mV)",
            "ppg": "Status, OXY100C (Status)",
            "slider": "Slider - TSD115 - Psychological assessment, AMI / HLT - A15 (number)"
        }

    builder = FeatureBuilder(df, sampling_rate, column_labels)
    intermediate_dataframes, _ = builder.process_signals()

    # Save each DataFrame from the intermediate_dataframes dictionary
    for key, intermediate_df in intermediate_dataframes.items():
        if intermediate_df is not None:  # Check if DataFrame is empty or None
            file_path = builder.save2path(intermediate_df, researcher_initials, participant_id, key)
            print(f"{key} features saved at {file_path}")
    
    events = builder._create_events()

    print("Data features and events created and saved!")
    
    return intermediate_dataframes, events

