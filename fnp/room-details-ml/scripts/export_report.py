from src.reports.generator import generate_report

def main():
    # Define the input parameters for the report
    room_details = {
        'number_of_days': 5,
        'area': 150,
        'walls': 4,
        'vertices': [(0, 0, 0), (0, 10, 0), (10, 10, 0), (10, 0, 0)],
        'blueprint': 'path/to/blueprint/image.png',
        'visualizations': ['path/to/visualization1.png', 'path/to/visualization2.png']
    }
    
    # Generate the report
    generate_report(room_details)

if __name__ == "__main__":
    main()