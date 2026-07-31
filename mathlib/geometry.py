from enum import Enum

class Shape(Enum):
    CIRCLE = 'circle'
    SQUARE = 'square'
    TRIANGLE = 'triangle'

def calculate_area(shape: Shape, **kwargs):
    """
    Calculate the area of a shape.

    Args:
        shape (Shape): The shape to calculate the area for.
        **kwargs: Additional keyword arguments depending on the shape.

    Returns:
        float: The calculated area.
    """
    if shape == Shape.CIRCLE:
        radius = kwargs.get('radius', 0)
        return 3.14 * radius ** 2
    elif shape == Shape.SQUARE:
        side = kwargs.get('side', 0)
        return side ** 2
    elif shape == Shape.TRIANGLE:
        base = kwargs.get('base', 0)
        height = kwargs.get('height', 0)
        return 0.5 * base * height
    else:
        raise ValueError('Invalid shape')

# Example usage:
print(calculate_area(Shape.CIRCLE, radius=5))  # Output: 78.5
print(calculate_area(Shape.SQUARE, side=4))  # Output: 16
print(calculate_area(Shape.TRIANGLE, base=3, height=6))  # Output: 9.0