# Room Details ML Project

This project is designed to predict room details such as the number of days to be worked, area, and walls using a machine learning model. It integrates various components to provide a comprehensive solution for room detail prediction and reporting.

## Project Structure

```
room-details-ml
├── src
│   ├── app.py                # Main entry point for the application
│   ├── ml
│   │   ├── __init__.py       # Initializes the ml module
│   │   ├── inference.py       # Contains RoomPredictor class for model inference
│   │   └── postprocess.py     # Functions for processing model output
│   ├── models
│   │   └── README.md          # Documentation for machine learning models
│   ├── utils
│   │   ├── visualization.py    # Functions for generating visualizations
│   │   └── geometry.py        # Utility functions for geometric calculations
│   └── reports
│       ├── generator.py       # Generates the final report
│       └── templates
│           └── report_template.html # HTML template for the report
├── notebooks
│   ├── 01-data-exploration.ipynb # Data exploration notebook
│   └── 02-modeling.ipynb      # Modeling and training notebook
├── scripts
│   ├── train.py               # Script for training the machine learning model
│   ├── predict.py             # Script for making predictions
│   └── export_report.py       # Script for generating the final report
├── web
│   ├── static
│   │   ├── css
│   │   │   └── styles.css     # CSS styles for the web report
│   │   └── js
│   │       └── report.js      # JavaScript for report interactivity
│   └── templates
│       └── report.html        # Main HTML page for the report
├── data
│   ├── raw                    # Folder for raw input data
│   └── processed              # Folder for processed data
├── reports
│   ├── figures                # Folder for generated figures
│   └── html                   # Folder for HTML reports
├── tests
│   └── test_inference.py      # Unit tests for the inference module
├── requirements.txt           # Project dependencies
├── .gitignore                 # Files to ignore in version control
└── README.md                  # Overview of the project
```

## Features

- **Machine Learning Model**: Predicts room details based on input parameters.
- **Data Exploration**: Jupyter notebooks for exploring and understanding the dataset.
- **Visualization**: Generates visualizations and blueprints for better understanding.
- **Reporting**: Creates comprehensive reports with images, visualizations, and HTML output.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd room-details-ml
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/app.py
   ```

4. Access the application in your web browser at `http://localhost:5000`.

## Usage

- Use the provided scripts to train the model, make predictions, and generate reports.
- Explore the notebooks for data exploration and modeling insights.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.