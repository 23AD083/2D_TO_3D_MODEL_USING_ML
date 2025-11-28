import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

# Load the dataset
def load_data(data_path):
    data = pd.read_csv(data_path)
    return data

# Preprocess the data
def preprocess_data(data):
    # Assuming 'area', 'walls', and 'days' are the features and 'room_details' is the target
    X = data[['area', 'walls', 'days']]
    y = data['room_details']
    return X, y

# Train the model
def train_model(X, y):
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

# Save the model
def save_model(model, model_path):
    joblib.dump(model, model_path)

def main():
    data_path = os.path.join('data', 'processed', 'room_data.csv')  # Adjust path as necessary
    model_path = os.path.join('models', 'room_predictor.pkl')  # Adjust path as necessary

    # Load and preprocess data
    data = load_data(data_path)
    X, y = preprocess_data(data)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model = train_model(X_train, y_train)

    # Save the trained model
    save_model(model, model_path)

if __name__ == "__main__":
    main()