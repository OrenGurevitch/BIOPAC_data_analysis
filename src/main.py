data_file = "C:\\Users\\oreng\\OneDrive - McGill University\\Documents\\Masters_Program\\Pilot Study\\recordings_pilot\\8_OG_pilot_tobii_biopac\\8_OG_pilot_July_25_2023.mat"
sampling_rate = 2000
excel_path = "C:\\Users\\oreng\\OneDrive - McGill University\\Documents\\Masters_Program\\Measurements\\BIOPAC\\analysis2excel\\analysis.xlsx"

from data.make_dataset import main as make_dataset
# Make the dataset and receive the DataFrame and sampling rate
df = make_dataset(data_file, sampling_rate, excel_path)

from features.build_features import main as build_features
# Build features using the received DataFrame and sampling rate
processed_dataframes, events = build_features(df, sampling_rate)
#print("ecg processed_dataframes: ", processed_dataframes['ecg'])
print("events: ", events)
from visualization.visualize import main as visualize
#Choose which features to visualize?
visualize(df, processed_dataframes, sampling_rate, excel_path, events, HRV=False, excel_table=True, ecg=False, rsp=False, eda=False, ppg=False, slider=False, rates_and_events=False)

#from src.visualization.gui import show_gui
#show_gui(processed_dataframes, sampling_rate, excel_path, events)
''' The following lines are commented out because they are not yet implemented
#from models.train_model import run as train_model
#from models.predict_model import run as predict_model
#from visualization.visualize import run as visualize

# Train the model
#train_model()

# Make predictions
#predict_model()
'''

print("Analysis complete!")

