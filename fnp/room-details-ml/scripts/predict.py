import sys
import json
import numpy as np
from src.ml.inference import RoomPredictor
from src.utils.visualization import plot_room_details
from src.utils.geometry import calculate_vertices
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    try:
        # Validate input data
        if 'area' not in data or 'walls' not in data or 'days' not in data:
            return jsonify({'error': 'Invalid input data'}), 400
        
        area = data['area']
        walls = data['walls']
        days = data['days']

        # Load the model and make predictions
        predictor = RoomPredictor()
        predictor.load_model('path/to/your/model')  # Update with actual model path
        prediction = predictor.predict(area, walls, days)

        # Calculate vertices for visualization
        vertices = calculate_vertices(area, walls)

        # Generate visualizations
        plot_room_details(prediction)

        return jsonify({
            'prediction': prediction,
            'vertices': vertices.tolist()  # Convert numpy array to list for JSON serialization
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)