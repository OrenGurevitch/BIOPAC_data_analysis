from gui.run_gui import main as run_gui
# Initialize the GUI and get the input values
data_file, sampling_rate, researcher_initials, participant_name, participant_id, HRV, excel_table, ecg, rsp, eda, ppg, slider, rates_and_events = run_gui()

from read.make_dataset import main as make_dataset
# Make the dataset and receive the DataFrame and sampling rate
df = make_dataset(data_file, sampling_rate, researcher_initials, participant_id)

from features.build_features import main as build_features
# Build features using the received DataFrame and sampling rate
processed_dataframes, events = build_features(df, sampling_rate, researcher_initials, participant_id)

from visualization.visualize import main as visualize
# Visualize the data using the received DataFrame, sampling rate, and other input values
visualize(df, processed_dataframes, sampling_rate, researcher_initials, participant_id, events, HRV, excel_table, ecg, rsp, eda, ppg, slider, rates_and_events)

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

