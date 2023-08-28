import neurokit2 as nk
import pandas as pd
import os
from datetime import datetime
from pathlib import Path

class FeatureBuilder:
    def __init__(self, df: pd.DataFrame, sampling_rate: int, column_labels: dict):
        self.df = df
        self.sampling_rate = sampling_rate
        self.column_labels = column_labels

    def _process(self, process_func, column_label):
        nk_processed_signals, _ = process_func(self.df[column_label], self.sampling_rate)
        return nk_processed_signals

    def _process_slider(self):
        column_label = "Slider - TSD115 - Psychological assessment, AMI / HLT - A15 (number)"
        if column_label in self.df.columns:
            slider_scores = self.df[column_label]
            filtered_signal = nk.signal_filter(slider_scores, method="savgol", sampling_rate=self.sampling_rate, lowcut=0.1, highcut=None)
            return pd.DataFrame({'slider': filtered_signal})
        else:
            return None

    def process_signals(self):
        ecg_processed = self._process(nk.ecg_process, self.column_labels['ecg'])
        rsp_processed = self._process(nk.rsp_process, self.column_labels['rsp'])
        eda_processed = self._process(nk.eda_process, self.column_labels['eda'])
        ppg_processed = self._process(nk.ppg_process, self.column_labels['ppg'])
        slider_processed = self._process_slider()

        events = self._create_events()

        processed_dataframes = {
            'ecg': ecg_processed,
            'rsp': rsp_processed,
            'eda': eda_processed,
            'ppg': ppg_processed,
            'slider': slider_processed
        }
        return processed_dataframes, events

    def _create_events(self):
        event_labels = ["Absorptive", "1stSilence", "Self-Chosen Absorptive", "2ndSilence", "Self-Chosen Non-absorptive", "3rdSilence"]
        event_labels_unique = [f"{label}_{i+1}" for i, label in enumerate(event_labels)]
        event_onsets_seconds = [0, 420, 600, 1020, 1200, 1620]
        event_onsets_indices = [int(i * self.sampling_rate) for i in event_onsets_seconds]
        return nk.events_create(event_onsets=event_onsets_indices, event_labels=event_labels_unique)
 
    def save_dataframe(self, df: pd.DataFrame, researcher_initials: str, feature_type: str):
        current_date = datetime.now().strftime("%Y_%m_%d")
        raw_excel_file_name = f"intermediate_data_{feature_type}_{researcher_initials}_{current_date}.csv"
        script_dir = Path(__file__).resolve().parent.parent
        data_folder = script_dir.parent / "data" / "interim"
        raw_excel_path = data_folder / raw_excel_file_name
        if not data_folder.exists():
            data_folder.mkdir(parents=True)
        df.to_csv(raw_excel_path)
        return raw_excel_path

def main(df: pd.DataFrame, sampling_rate: int, researcher_initials: str):
    print("Building features...")
    
    column_labels = {
        "eda": "EDA100C (microsiemens)",
        "rsp": "RSP100C (Volts)",
        "ecg": "ECG100C (mV)",
        "ppg": "Status, OXY100C (Status)"
    }
    
    builder = FeatureBuilder(df, sampling_rate, column_labels)
    intermediate_dataframes, _ = builder.process_signals()

    # Save each DataFrame from the intermediate_dataframes dictionary
    for key, intermediate_df in intermediate_dataframes.items():
        if intermediate_df is not None:  # Check if DataFrame is empty or None
            file_path = builder.save_dataframe(intermediate_df, researcher_initials, key)
            print(f"{key} features saved at {file_path}")
    
    events = builder._create_events()
    
    print("Data features and events created and saved!")
    
    return intermediate_dataframes, events

