import numpy as np
import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt

class visualize:
    def __init__(self, df, sampling_rate, excel_path, ):
        self.df = df
        self.sampling_rate = sampling_rate
        self.time = self.generate_time(df)

    def generate_time(self, df):
        """Generate time array in minutes."""
        return np.arange(len(df)) / self.sampling_rate / 60

    def annotate_events(self, events):
        event_onsets_indices = events['onset']
        event_labels = events['label']
        #Mark event moments on the plot
        onset_minutes = [onset / self.sampling_rate / 60 for onset in event_onsets_indices]
        for onset, label in zip(onset_minutes, event_labels):
            plt.axvline(x=onset, color='red', linestyle='--', alpha=0.7)
            plt.text(onset, plt.gca().get_ylim()[1], label, rotation=45, color='red')
        
    def rates_and_events(self, onset_indices, labels):

        plt.figure(figsize=(15, 12))
        plt.suptitle("Data Visualization", fontsize=20)

        # Heart Rate (ECG) subplot        
        plt.subplot(4, 1, 1)
        plt.plot(self.generate_time(df), ecg_signals['ECG_Rate'], color='cyan', linewidth=0.5)
        plt.title("Heart Rate (BPM)")
        analyzer.annotate_events(event_onsets_indices, event_labels)

        # Breathing Rate (RSP) subplot
        plt.subplot(4, 1, 2)
        plt.plot(self.generate_time(df), rsp_signals['RSP_Rate'], color='blue', linewidth=0.5)
        plt.title("Breathing Rate")
        analyzer.annotate_events(event_onsets_indices, event_labels)

        # SCR (EDA) subplot
        plt.subplot(4, 1, 3)
        plt.plot(self.generate_time(df), eda_signals["EDA_Phasic"], color='green', linewidth=0.5)
        plt.title("SCR (EDA)")
        analyzer.annotate_events(event_onsets_indices, event_labels)

        # SCL (EDA) subplot
        plt.subplot(4, 1, 4)
        plt.plot(self.generate_time(df), eda_signals["EDA_Tonic"], color='orange', linewidth=0.5)
        plt.title("SCL (EDA)")
        analyzer.annotate_events(event_onsets_indices, event_labels)

        plt.tight_layout()
        plt.show()

    def HRV_plot(self):
        # Processing ECG data for HRV
        ecg = self.df["ECG100C (mV)"].values
        peaks, _ = nk.ecg_peaks(ecg, sampling_rate=self.sampling_rate)
        nk.hrv(peaks, sampling_rate=self.sampling_rate, show=False)

    def plot_procesed(self, ecg, rsp, eda, ppg, slider, rates_and_events):
        if ecg==True:
            nk.ecg_plot(signals, sampling_rate=self.sampling_rate)
            plt.show()
        if rsp==True:
            nk.rsp_plot(signals, sampling_rate=self.sampling_rate)
            plt.show()
        if eda==True:
            nk.eda_plot(signals, sampling_rate=self.sampling_rate)
            plt.show()
        if ppg==True:
            ppg_plot(signals, sampling_rate=self.sampling_rate)
            plt.show()

        if slider==True:
            plt.plot(self.time, self.df["Slider - TSD115 - Psychological assessment, AMI / HLT - A15 (number)"])
            plt.xlabel("Time (minutes)")
            plt.ylabel("Slider Score")
            plt.title("Filtered Slider Score Over Time")
            plt.show()
    
    def analysis_dataframe(self, analysis_function, signals, events, SAMPLING_RATE, excel_path=None):
        results_list = []

        for onset, label in zip(events["onset"], events["label"]):
            offset = onset + 7 * 60 * SAMPLING_RATE if "Silence" not in label else onset + 3 * 60 * SAMPLING_RATE
            epoch = signals.iloc[onset:offset]

            # Check if the epoch is empty, and continue if it is
            if epoch.empty:
                print(f"Warning: Empty epoch for label {label}")
                continue

            # Analyze the epoch with the provided analysis function
            result = analysis_function(epoch, sampling_rate=SAMPLING_RATE)

            # Adding the label of the event to the result
            result.insert(0, 'Event_Label', label)

            # Append to the results list
            results_list.append(result)

        # Convert results list to DataFrame
        results_df = pd.concat(results_list, ignore_index=True)

        # Transpose the DataFrame (this will swap the rows and columns)
        results_df = results_df.transpose()

        # Print the results
        print(results_df)

    def excel_table(self):

        eda_analysis_df = analysis_dataframe(nk.eda_intervalrelated, eda_signals, events)
        ecg_analysis_df = analysis_dataframe(nk.ecg_analyze, ecg_signals, events)
        rsp_analysis_df = analysis_dataframe(nk.rsp_intervalrelated, rsp_signals, events)

        # Save all data frames to the same Excel file in different sheets
        with pd.ExcelWriter(path4excel) as writer:
            eda_analysis_df.to_excel(writer, sheet_name='EDA_Analysis')
            ecg_analysis_df.to_excel(writer, sheet_name='ECG_Analysis')
            rsp_analysis_df.to_excel(writer, sheet_name='RSP_Analysis')

        print(f"Results saved to Excel at {excel_path}")
    

def main(processed_dataframes: pd.DataFrame, sampling_rate: int, sampling_rate == 2000, excel_path, events, HRV == False, excel_table == False, ecg == False, rsp == False, eda == False, ppg == False, slider == False, rates_and_events == False):
    # Analyze data and get data frames
    plot_procesed(ecg, rsp, eda, ppg, slider, rates_and_events)

    if HRV==True:
        HRV_plot()

    if excel_table==True:
        excel_table()

##############################################################################################################
class PlotProcessed:
    def __init__(self, df, sampling_rate):
        self.df = df
        self.sampling_rate = sampling_rate
        self.time = self.generate_time(df)

    def plot_procesed(self, ecg, rsp, eda, ppg, slider, rates_and_events):
        if ecg==True:
            nk.ecg_plot(signals, sampling_rate=self.sampling_rate)
            plt.show()
        if rsp==True:
            nk.rsp_plot(signals, sampling_rate=self.sampling_rate)
            plt.show()
        if eda==True:
            nk.eda_plot(signals, sampling_rate=self.sampling_rate)
            plt.show()
        if ppg==True:
            ppg_plot(signals, sampling_rate=self.sampling_rate)
            plt.show()

        if slider==True:
            plt.plot(self.time, self.df["Slider - TSD115 - Psychological assessment, AMI / HLT - A15 (number)"])
            plt.xlabel("Time (minutes)")
            plt.ylabel("Slider Score")
            plt.title("Filtered Slider Score Over Time")
            plt.show()

    def annotate_events(self, events):
        event_onsets_indices = events['onset']
        event_labels = events['label']
        #Mark event moments on the plot
        onset_minutes = [onset / self.sampling_rate / 60 for onset in event_onsets_indices]
        for onset, label in zip(onset_minutes, event_labels):
            plt.axvline(x=onset, color='red', linestyle='--', alpha=0.7)
            plt.text(onset, plt.gca().get_ylim()[1], label, rotation=45, color='red')

# You can use these methods as:
plot_processed = PlotProcessed(df, sampling_rate)
plot_processed.plot_procesed(ecg, rsp, eda, ppg, slider, rates_and_events)
