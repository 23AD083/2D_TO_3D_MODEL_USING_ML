def plot_room_details(room_data):
    import matplotlib.pyplot as plt
    import numpy as np

    # Extracting room details
    days = room_data['days']
    area = room_data['area']
    walls = room_data['walls']

    # Creating a bar chart for room details
    labels = ['Days', 'Area', 'Walls']
    values = [days, area, walls]

    plt.bar(labels, values, color=['blue', 'green', 'orange'])
    plt.title('Room Details')
    plt.ylabel('Values')
    plt.grid(axis='y')

    # Save the plot
    plt.savefig('reports/figures/room_details.png')
    plt.close()

def create_blueprint(room_dimensions):
    import matplotlib.pyplot as plt

    # Assuming room_dimensions is a tuple (length, width)
    length, width = room_dimensions

    # Create a simple rectangle to represent the room
    plt.figure(figsize=(length/10, width/10))
    plt.plot([0, length, length, 0, 0], [0, 0, width, width, 0], 'b-')
    plt.fill([0, length, length, 0], [0, 0, width, width], color='lightblue', alpha=0.5)
    plt.title('Room Blueprint')
    plt.xlim(-1, length + 1)
    plt.ylim(-1, width + 1)
    plt.gca().set_aspect('equal', adjustable='box')

    # Save the blueprint
    plt.savefig('reports/figures/blueprint.png')
    plt.close()