from data.make_dataset import run as make_dataset
from features.build_features import run as build_features
from models.train_model import run as train_model
from models.predict_model import run as predict_model
from visualization.visualize import run as visualize

# Make the dataset
make_dataset()

# Build features
build_features()

# Train the model
train_model()

# Make predictions
predict_model()

# Create visualizations
visualize()

print("Analysis complete!")
