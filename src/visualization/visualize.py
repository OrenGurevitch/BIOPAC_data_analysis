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

class SaveExcelTableAndPlotBars:
    def __init__(self, processed_dataframes, events, sampling_rate, researcher_initials, participant_id):
        self.events = events
        self.sampling_rate = sampling_rate
        self.processed_dataframes = processed_dataframes
        self.ecg_signals = self.processed_dataframes['ecg']
        self.rsp_signals = self.processed_dataframes['rsp']
        self.eda_signals = self.processed_dataframes['eda']
        self.researcher_initials = researcher_initials
        self.participant_id = participant_id

    def analysis_dataframe(self, analysis_function, signal):
        results_list = []

        for i, (onset, label) in enumerate(zip(self.events["onset"], self.events["label"])):

            # Ignore events with the label "pci"
            if "pci" in label.lower():
                continue # Skip this iteration of the loop

            print(label)
            #get the offset of the events
            if i < len(self.events["onset"]) - 1:
                offset = self.events["onset"][i + 1]
            else:
                offset = len(signal) # Last event

            print(f"onset: {onset}, offset: {offset}")
            epoch = signal.iloc[onset:offset] # Get the epoch, onset to offset

            if epoch.empty:
                print(f"Warning: Empty epoch for label {label}")
                continue
            # Run the analysis function on the epoch
            result = analysis_function(epoch, sampling_rate=self.sampling_rate)
            result.insert(0, 'Event_Label', label)
            results_list.append(result)

        results_df = pd.concat(results_list, ignore_index=True) # Concatenate the list of dataframes into one dataframe
        results_df = results_df.set_index("Event_Label").transpose() # Transpose the dataframe so that the events are the columns and the features are the rows

        print(results_df)
        return results_df

    def analysis_data_signals(self):
        eda_analysis_df = self.analysis_dataframe(nk.eda_intervalrelated, self.eda_signals)
        ecg_analysis_df = self.analysis_dataframe(nk.ecg_analyze, self.ecg_signals)
        rsp_analysis_df = self.analysis_dataframe(nk.rsp_intervalrelated, self.rsp_signals)

        return eda_analysis_df, ecg_analysis_df, rsp_analysis_df

    def save2path(self, eda_analysis_df, ecg_analysis_df, rsp_analysis_df, feature_type: str):
        current_date = datetime.now().strftime("%Y_%m_%d")
        excel_file_name = f"processed_data_{feature_type}_{self.participant_id}_{self.researcher_initials}_{current_date}.csv"
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

    def plot_bargraphs(self, dataframe, feature_type: str):
        '''
        The function plots bar graphs for important rows in each dataframe based on feature type.
        '''
        figures_folder = create_folder_for_figures(self.researcher_initials, self.participant_id)

        important_rows = []  # Rows you want to focus on for plotting

        # Define the important rows for each feature type
        if feature_type == "rsp":
            important_rows = ['RSP_Rate_Mean', 'RRV_RMSSD']
        elif feature_type == "eda":
            important_rows = ['SCR_Peaks_N', 'EDA_Sympathetic']
        elif feature_type == "ecg":
            important_rows = ['ECG_Rate_Mean', 'HRV_MeanNN']
        else:
            print(f"Unknown feature_type: {feature_type}")
            return

        print(f"Plotting bar graphs for {feature_type}...")
        
        for row in important_rows:
            print(f"Plotting bar graph for {row}...")
            if row in dataframe.index:
                row_data = dataframe.loc[row]
                # Remove square brackets, if any, and convert to float
                row_data = row_data.apply(lambda x: x[0] if isinstance(x, list) and len(x) == 1 else x) # Remove square brackets, if any
                row_data = row_data.astype(float)  # Ensure data is in float format for plotting
            else:
                print(f"Row {row} not found in dataframe.")
                continue

            # Plot the bar graph
            plt.figure(figsize=(14, 8))  # Increase the figure size
            plt.bar(dataframe.columns.tolist(), row_data.values)
            plt.xlabel('Blocks')
            plt.ylabel(row)
            plt.title(f"{row} for {self.participant_id}")

            # Rotate x-axis labels
            plt.xticks(rotation=45)  # Rotates X-Axis Ticks by 45-degrees

            # Adjust the layout
            plt.tight_layout()

            # Save the plot
            plot_path = figures_folder / f"{row}_{feature_type}_{self.participant_id}_{self.researcher_initials}.png"
            plt.savefig(plot_path)
            plt.close()

        print(f"Plots saved at {figures_folder}")


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
        excel_table_obj = SaveExcelTableAndPlotBars(processed_dataframes, events, sampling_rate, researcher_initials, participant_id)
        eda_analysis_df, ecg_analysis_df, rsp_analysis_df = excel_table_obj.analysis_data_signals()
        excel_table_obj.save2path(eda_analysis_df, ecg_analysis_df, rsp_analysis_df, "excel_table")

        # In order to change which rows are plotted, change the important_rows list in the plot_bargraphs function
        excel_table_obj.plot_bargraphs(rsp_analysis_df, "rsp")
        excel_table_obj.plot_bargraphs(eda_analysis_df, "eda")
        excel_table_obj.plot_bargraphs(ecg_analysis_df, "ecg")
        
    
    print("Data visualization complete!")