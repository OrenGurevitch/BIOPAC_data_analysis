import numpy as np
import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt
import os
from datetime import datetime
from pathlib import Path

class NKPlotProcessed:
    def __init__(self, df, sampling_rate, processed_dataframes, researcher_initials, participant_id):
        self.df = df
        self.sampling_rate = sampling_rate
        self.processed_dataframes = processed_dataframes
        self.time = self.generate_time()  
        self.researcher_initials = researcher_initials
        self.participant_id = participant_id

    def generate_time(self):
        """Generate time array in minutes."""
        return np.arange(len(self.df)) / self.sampling_rate / 60
    
    def plot_processed(self, ecg=False, rsp=False, eda=False, ppg=False, slider=False):
        figures_folder = create_folder_for_figures(self.researcher_initials, self.participant_id)
        if ecg:
            print(self.processed_dataframes['ecg'])
            nk.ecg_plot(self.processed_dataframes['ecg'], sampling_rate=self.sampling_rate)
            plt.savefig(figures_folder / "ecg_plot.png")
            plt.show()
        if rsp:
            nk.rsp_plot(self.processed_dataframes['rsp'], sampling_rate=self.sampling_rate)
            plt.savefig(figures_folder / "rsp_plot.png")
            plt.show()
        if eda:
            nk.eda_plot(self.processed_dataframes['eda'], sampling_rate=self.sampling_rate)
            plt.savefig(figures_folder / "eda_plot.png")
            plt.show()
        if ppg:
            nk.ppg_plot(self.processed_dataframes['ppg'], sampling_rate=self.sampling_rate)
            plt.savefig(figures_folder / "ppg_plot.png")
            plt.show()
        if slider:
            plt.plot(self.time, self.processed_dataframes['slider'])
            plt.xlabel("Time (minutes)")
            plt.ylabel("Slider Score")
            plt.title("Filtered Slider Score Over Time")
            plt.savefig(figures_folder / "slider_plot.png")
            plt.show()
        
class HRVPlot:
    def __init__(self, df, sampling_rate, researcher_initials, participant_id):
        self.df = df
        self.sampling_rate = sampling_rate
        self.researcher_initials = researcher_initials
        self.participant_id = participant_id

    def plot(self):
        # Processing ECG data for HRV is like making a special dish with extra steps.
        ecg = self.df["ECG100C (mV)"].values
        peaks, info = nk.ecg_peaks(ecg, sampling_rate=self.sampling_rate)
        nk.hrv(peaks, sampling_rate=self.sampling_rate, show=True)

        figures_folder = create_folder_for_figures(self.researcher_initials, self.participant_id)
        plt.savefig(figures_folder / "hrv_plot.png")

class ExcelTable:
    def __init__(self, processed_dataframes, events, sampling_rate):
        self.events = events
        self.sampling_rate = sampling_rate
        self.processed_dataframes = processed_dataframes
        self.ecg_signals = self.processed_dataframes['ecg']
        self.rsp_signals = self.processed_dataframes['rsp']
        self.eda_signals = self.processed_dataframes['eda']

    def analysis_dataframe(self, analysis_function, signal):
        results_list = []

        for i, (onset, label) in enumerate(zip(self.events["onset"], self.events["label"])):

            # Ignore events with the label "pci"
            if "pci" in label.lower():
                continue # Skip this iteration of the loop

            print(label)
            if i < len(self.events["onset"]) - 1:
                offset = self.events["onset"][i + 1]
            else:
                offset = len(signal)

            print(f"onset: {onset}, offset: {offset}")
            epoch = signal.iloc[onset:offset]

            if epoch.empty:
                print(f"Warning: Empty epoch for label {label}")
                continue

            result = analysis_function(epoch, sampling_rate=self.sampling_rate) 
            result.insert(0, 'Event_Label', label)
            results_list.append(result)

        results_df = pd.concat(results_list, ignore_index=True)
        results_df = results_df.transpose()
        print(results_df)
        return results_df

    def analysis_data_signals(self):
        eda_analysis_df = self.analysis_dataframe(nk.eda_intervalrelated, self.eda_signals)
        ecg_analysis_df = self.analysis_dataframe(nk.ecg_analyze, self.ecg_signals)
        rsp_analysis_df = self.analysis_dataframe(nk.rsp_intervalrelated, self.rsp_signals)

        return eda_analysis_df, ecg_analysis_df, rsp_analysis_df

    def save2path(self, eda_analysis_df, ecg_analysis_df, rsp_analysis_df, researcher_initials: str, participant_id: str, feature_type: str):
        current_date = datetime.now().strftime("%Y_%m_%d")
        excel_file_name = f"processed_data_{feature_type}_{participant_id}_{researcher_initials}_{current_date}.csv"
        script_dir = Path(__file__).resolve().parent.parent
        data_folder = script_dir.parent / "data" / "processed"
        excel_path = data_folder / excel_file_name
        if not data_folder.exists():
            data_folder.mkdir(parents=True)

        with pd.ExcelWriter(excel_path) as writer:
            eda_analysis_df.to_excel(writer, sheet_name='EDA_Analysis')
            ecg_analysis_df.to_excel(writer, sheet_name='ECG_Analysis')
            rsp_analysis_df.to_excel(writer, sheet_name='RSP_Analysis')

        print(f"Results saved to Excel at {excel_path}")


class RatesAndEvents:
    def __init__(self, sampling_rate, df, events, processed_dataframes, researcher_initials, participant_id):
        self.sampling_rate = sampling_rate
        self.time = self.generate_time(df)
        self.events = events
        self.df = df
        self.processed_dataframes = processed_dataframes
        self.researcher_initials = researcher_initials
        self.participant_id = participant_id
    
    def generate_time(self, df):
        """Generate time array in minutes."""
        return np.arange(len(df)) / self.sampling_rate / 60

    def annotate_events(self):
        event_onsets_indices = self.events['onset']
        event_labels = self.events['label']
        # Mark event moments on the plot
        onset_minutes = [onset / self.sampling_rate / 60 for onset in event_onsets_indices]
        for onset, label in zip(onset_minutes, event_labels):
            plt.axvline(x=onset, color='red', linestyle='--', alpha=0.7)
            plt.text(onset, plt.gca().get_ylim()[1], label, rotation=45, color='red')
        
    def plot_rates_and_events(self):

        plt.figure(figsize=(15, 12))
        plt.suptitle("Data Visualization", fontsize=20)

        # Heart Rate (ECG) subplot        
        plt.subplot(5, 1, 1)
        plt.plot(self.time, self.processed_dataframes['ecg']['ECG_Rate'], color='cyan', linewidth=0.5)
        plt.title("Heart Rate (BPM)")
        self.annotate_events()

        # Breathing Rate (RSP) subplot
        plt.subplot(5, 1, 2)
        plt.plot(self.time, self.processed_dataframes['rsp']['RSP_Rate'], color='blue', linewidth=0.5) # Fixed 'ecg' to 'rsp'
        plt.title("Breathing Rate")
        self.annotate_events()

        # SCR (EDA) subplot
        plt.subplot(5, 1, 3)
        plt.plot(self.time, self.processed_dataframes['eda']["EDA_Phasic"], color='green', linewidth=0.5)
        plt.title("SCR (EDA)")
        self.annotate_events()

        # SCL (EDA) subplot
        plt.subplot(5, 1, 4)
        plt.plot(self.time, self.processed_dataframes['eda']["EDA_Tonic"], color='orange', linewidth=0.5)
        plt.title("SCL (EDA)")
        self.annotate_events()

        # Slider subplot
        plt.subplot(5,1,5)
        plt.plot(self.time, self.processed_dataframes['slider'], color='purple', linewidth=0.5)
        plt.title("Slider Score")
        self.annotate_events()

        plt.tight_layout()

        # Get folder path to save figures
        folder_path = create_folder_for_figures(self.researcher_initials, self.participant_id)
        # Create figure name and save
        plt.savefig(folder_path / "rates&events_plot.png")
        plt.show()


# Utility function to create and return the new directory path
def create_folder_for_figures(researcher_initials, participant_id):
    current_date = datetime.now().strftime("%Y_%m_%d")
    folder_name = f"{participant_id}_{researcher_initials}_{current_date}"
    script_dir = Path(__file__).resolve().parent.parent
    figures_folder = script_dir.parent / "reports" / "figures" / folder_name
    if not figures_folder.exists():
        figures_folder.mkdir(parents=True) 
    return figures_folder

def main(df: pd.DataFrame, processed_dataframes: pd.DataFrame, sampling_rate: int, researcher_initials: str, participant_id: str, events, HRV=False, excel_table=False, ecg=False, rsp=False, eda=False, ppg=False, slider=False, rates_and_events=False):
    print("Visualizing data...")
    
    plot_processed = NKPlotProcessed(df, sampling_rate, processed_dataframes, researcher_initials, participant_id)
    plot_processed.plot_processed(ecg, rsp, eda, ppg, slider)

    if rates_and_events:
        rates_and_events_plotter = RatesAndEvents(sampling_rate, df, events, processed_dataframes, researcher_initials, participant_id)
        rates_and_events_plotter.plot_rates_and_events()

    if HRV:
        hrv_plot = HRVPlot(df, sampling_rate, researcher_initials, participant_id)
        hrv_plot.plot()

    if excel_table:
        excel_table_obj = ExcelTable(processed_dataframes, events, sampling_rate)
        eda_analysis_df, ecg_analysis_df, rsp_analysis_df = excel_table_obj.analysis_data_signals()
        excel_table_obj.save2path(eda_analysis_df, ecg_analysis_df, rsp_analysis_df, researcher_initials, participant_id, "excel_table")
    
    print("Data visualization complete!")