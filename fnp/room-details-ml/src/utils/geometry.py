def calculate_vertices(length, width, height):
    """
    Calculate the vertices of a rectangular room given its dimensions.

    Parameters:
    length (float): The length of the room.
    width (float): The width of the room.
    height (float): The height of the room.

    Returns:
    list: A list of tuples representing the vertices (x, y, z) of the room.
    """
    return [
        (0, 0, 0),
        (length, 0, 0),
        (length, width, 0),
        (0, width, 0),
        (0, 0, height),
        (length, 0, height),
        (length, width, height),
        (0, width, height)
    ]

def area_of_room(length, width):
    """
    Calculate the area of a rectangular room.

    Parameters:
    length (float): The length of the room.
    width (float): The width of the room.

    Returns:
    float: The area of the room.
    """
    return length * width