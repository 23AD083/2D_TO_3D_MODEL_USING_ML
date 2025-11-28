# Machine Learning Models for Room Details Prediction

This directory contains the machine learning models used in the project for predicting various room details such as the number of days to be worked, area, and walls.

## Model Architecture

The models implemented in this project utilize a combination of regression techniques to accurately predict room specifications based on input features. The architecture is designed to handle various types of input data, including numerical and categorical features.

## Training Process

The models are trained using a dataset that includes historical data on room dimensions and specifications. The training process involves the following steps:

1. **Data Preprocessing**: The raw data is cleaned and transformed into a suitable format for training.
2. **Feature Engineering**: Relevant features are extracted and engineered to improve model performance.
3. **Model Selection**: Various regression models are evaluated, and the best-performing model is selected based on validation metrics.
4. **Hyperparameter Tuning**: The selected model undergoes hyperparameter tuning to optimize its performance.
5. **Model Evaluation**: The final model is evaluated on a test set to ensure its predictive accuracy.

## Usage

To use the models in this project, you can import the `RoomPredictor` class from the `inference.py` file in the `ml` module. This class provides methods for loading the trained model and making predictions based on new input data.

## Future Work

Future improvements may include:

- Incorporating additional features for better predictions.
- Exploring advanced machine learning techniques such as ensemble methods.
- Enhancing the user interface for easier interaction with the model predictions.