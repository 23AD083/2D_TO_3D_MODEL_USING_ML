import unittest
from src.ml.inference import RoomPredictor

class TestRoomPredictor(unittest.TestCase):

    def setUp(self):
        self.predictor = RoomPredictor()
        self.predictor.load_model('path/to/model')  # Adjust the path as necessary

    def test_predict(self):
        input_data = {
            'days': 5,
            'area': 100,
            'walls': 4
        }
        prediction = self.predictor.predict(input_data)
        self.assertIsNotNone(prediction)
        self.assertIn('estimated_cost', prediction)
        self.assertIn('room_dimensions', prediction)

    def test_invalid_input(self):
        invalid_input = {
            'days': -1,
            'area': 0,
            'walls': 4
        }
        with self.assertRaises(ValueError):
            self.predictor.predict(invalid_input)

if __name__ == '__main__':
    unittest.main()