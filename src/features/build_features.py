import neurokit2 as nk
import pandas as pd

class FeatureBuilder:
    def __init__(self, df: pd.DataFrame, sampling_rate: int):
        self.df = df
        self.sampling_rate = sampling_rate

    def process_signals(self):
        ecg_signals, _ = nk.ecg_process(self.df["ECG100C (mV)"], self.sampling_rate)
        rsp_signals, _ = nk.rsp_process(self.df["RSP100C (Volts)"], self.sampling_rate)
        eda_signals, _ = nk.eda_process(self.df["EDA100C (microsiemens)"], self.sampling_rate)
        ppg_signals, _ = nk.ppg_process(self.df["Status, OXY100C (Status)"], self.sampling_rate)
        slider_scores = self.df["Slider - TSD115 - Psychological assessment, AMI / HLT - A15 (number)"].values

        # Processing ECG data for HRV
        ecg = self.df["ECG100C (mV)"].values
        peaks, _ = nk.ecg_peaks(ecg, sampling_rate=self.sampling_rate)
        nk.hrv(peaks, sampling_rate=self.sampling_rate, show=False)

        event_labels = ["Absorptive", "1stSilence", "Self-Chosen Absorptive", "2ndSilence", "Self-Chosen Non-absorptive", "3rdSilence"]
        event_labels_unique = [f"{label}_{i+1}" for i, label in enumerate(event_labels)]
        event_onsets_seconds = [0, 420, 600, 1020, 1200, 1620]
        event_onsets_indices = [int(i * self.sampling_rate) for i in event_onsets_seconds]
        events = nk.events_create(event_onsets=event_onsets_indices, event_labels=event_labels_unique)

        return ecg_signals, rsp_signals, eda_signals, ppg_signals, events, slider_scores
    
def main(df: pd.DataFrame, sampling_rate: int):
    builder = FeatureBuilder(df, sampling_rate)
    print("Features created!")
    return builder.process_signals()
