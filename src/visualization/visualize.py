import numpy as np
import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt

class NKPlotProcessed:
    def __init__(self, df, sampling_rate, processed_dataframes):
        self.df = df
        self.sampling_rate = sampling_rate
        self.processed_dataframes = processed_dataframes
        self.time = self.generate_time()  

    def generate_time(self):
        """Generate time array in minutes."""
        return np.arange(len(self.df)) / self.sampling_rate / 60
    
    def plot_processed(self, ecg=False, rsp=False, eda=False, ppg=False, slider=False):
        if ecg:
            nk.ecg_plot(self.processed_dataframes['ecg'], sampling_rate=self.sampling_rate)
            plt.show()
        if rsp:
            nk.rsp_plot(self.processed_dataframes['rsp'], sampling_rate=self.sampling_rate)
            plt.show()
        if eda:
            nk.eda_plot(self.processed_dataframes['eda'], sampling_rate=self.sampling_rate)
            plt.show()
        if ppg:
            nk.ppg_plot(self.processed_dataframes['ppg'], sampling_rate=self.sampling_rate)
            plt.show()
        if slider:
            plt.plot(self.time, self.processed_dataframes['slider'])
            plt.xlabel("Time (minutes)")
            plt.ylabel("Slider Score")
            plt.title("Filtered Slider Score Over Time")
            plt.show()

class HRVPlot:
    def __init__(self, df, sampling_rate):
        self.df = df
        self.sampling_rate = sampling_rate

    def plot(self):
        # Processing ECG data for HRV is like making a special dish with extra steps.
        ecg = self.df["ECG100C (mV)"].values
        peaks, info = nk.ecg_peaks(ecg, sampling_rate=self.sampling_rate)
        nk.hrv(peaks, sampling_rate=self.sampling_rate, show=False)  # show=False to avoid showing the plot
        plt.show()

class ExcelTable:
    def __init__(self, processed_dataframes, events, sampling_rate, excel_path=None):
        self.events = events
        self.sampling_rate = sampling_rate
        self.excel_path = excel_path
        self.processed_dataframes = processed_dataframes
        self.ecg_signals = self.processed_dataframes['ecg']
        self.rsp_signals = self.processed_dataframes['rsp']
        self.eda_signals = self.processed_dataframes['eda']
    
    def analysis_dataframe(self, analysis_function, signal, events):
        results_list = []

        for onset, label in zip(self.events["onset"], self.events["label"]):
            offset = onset + 7 * 60 * self.sampling_rate if "Silence" not in label else onset + 3 * 60 * self.sampling_rate
            epoch = self.signals.iloc[onset:offset]

            if epoch.empty:
                print(f"Warning: Empty epoch for label {label}")
                continue

            result = self.analysis_function(epoch, sampling_rate=self.sampling_rate)
            result.insert(0, 'Event_Label', label)
            results_list.append(result)

        results_df = pd.concat(results_list, ignore_index=True)
        results_df = results_df.transpose()
        print(results_df)

    def save_to_excel(self, path4excel, eda_signals, ecg_signals, rsp_signals, events):
        eda_analysis_df = self.analysis_dataframe(nk.eda_intervalrelated, self.eda_signals, events)
        ecg_analysis_df = self.analysis_dataframe(nk.ecg_analyze, self.ecg_signals, events)
        rsp_analysis_df = self.analysis_dataframe(nk.rsp_intervalrelated, self.rsp_signals, events)

        with pd.ExcelWriter(path4excel) as writer:
            eda_analysis_df.to_excel(writer, sheet_name='EDA_Analysis')
            ecg_analysis_df.to_excel(writer, sheet_name='ECG_Analysis')
            rsp_analysis_df.to_excel(writer, sheet_name='RSP_Analysis')

        print(f"Results saved to Excel at {self.excel_path}")

class RatesAndEvents:
    def __init__(self, sampling_rate, df, events, processed_dataframes):
        self.sampling_rate = sampling_rate
        self.time = self.generate_time(df)
        self.events = events
        self.df = df
        self.processed_dataframes = processed_dataframes
    
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
        plt.subplot(4, 1, 1)
        plt.plot(self.time, self.processed_dataframes['ecg']['ECG_Rate'], color='cyan', linewidth=0.5)
        plt.title("Heart Rate (BPM)")
        self.annotate_events()

        # Breathing Rate (RSP) subplot
        plt.subplot(4, 1, 2)
        plt.plot(self.time, self.processed_dataframes['rsp']['RSP_Rate'], color='blue', linewidth=0.5) # Fixed 'ecg' to 'rsp'
        plt.title("Breathing Rate")
        self.annotate_events()

        # SCR (EDA) subplot
        plt.subplot(4, 1, 3)
        plt.plot(self.time, self.processed_dataframes['eda']["EDA_Phasic"], color='green', linewidth=0.5)
        plt.title("SCR (EDA)")
        self.annotate_events()

        # SCL (EDA) subplot
        plt.subplot(4, 1, 4)
        plt.plot(self.time, self.processed_dataframes['eda']["EDA_Tonic"], color='orange', linewidth=0.5)
        plt.title("SCL (EDA)")
        self.annotate_events()

        plt.tight_layout()
        plt.show()

def main(df: pd.DataFrame, processed_dataframes: pd.DataFrame, sampling_rate: int, excel_path, events, HRV=False, excel_table=False, ecg=False, rsp=False, eda=False, ppg=False, slider=False, rates_and_events=False):
    print("Visualizing data...")
    plot_processed = NKPlotProcessed(df, sampling_rate, processed_dataframes)
    plot_processed.plot_processed(ecg, rsp, eda, ppg, slider)

    if rates_and_events:
        rates_and_events_plotter = RatesAndEvents(sampling_rate, df, events, processed_dataframes)
        rates_and_events_plotter.plot_rates_and_events()

    if HRV:
        hrv_plot = HRVPlot(df, sampling_rate)
        hrv_plot.plot()

    if excel_table:
        excel_table_obj = ExcelTable(processed_dataframes, events, sampling_rate, excel_path)
        excel_table_obj.save_to_excel()

    print("Data visualization complete!")
