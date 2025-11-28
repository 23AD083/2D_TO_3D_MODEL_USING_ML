def format_predictions(predictions):
    formatted = []
    for pred in predictions:
        formatted.append({
            'area': round(pred['area'], 2),
            'walls': pred['walls'],
            'days_to_work': pred['days_to_work']
        })
    return formatted

def validate_input(input_data):
    if not isinstance(input_data, dict):
        raise ValueError("Input data must be a dictionary.")
    
    required_keys = ['length', 'width', 'height']
    for key in required_keys:
        if key not in input_data:
            raise ValueError(f"Missing required input: {key}")
    
    if input_data['length'] <= 0 or input_data['width'] <= 0 or input_data['height'] <= 0:
        raise ValueError("Dimensions must be positive values.")
    
    return True