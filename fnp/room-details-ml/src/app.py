from flask import Flask, request, jsonify, render_template
from ml.inference import RoomPredictor
from utils.visualization import plot_room_details, create_blueprint
import os

app = Flask(__name__)
model = RoomPredictor()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    days = data.get('days')
    area = data.get('area')
    walls = data.get('walls')

    if not all([days, area, walls]):
        return jsonify({'error': 'Missing input data'}), 400

    prediction = model.predict(days, area, walls)
    plot_path = plot_room_details(prediction)
    blueprint_path = create_blueprint(prediction)

    return jsonify({
        'prediction': prediction,
        'plot_path': plot_path,
        'blueprint_path': blueprint_path
    })

if __name__ == '__main__':
    app.run(debug=True)