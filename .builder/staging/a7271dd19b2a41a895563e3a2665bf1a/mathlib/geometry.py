import math

def area(shape, **kwargs):
    if shape == 'circle':
        return math.pi * kwargs['radius'] ** 2
    elif shape == 'rectangle':
        return kwargs['length'] * kwargs['width']
    elif shape == 'triangle':
        return 0.5 * kwargs['base'] * kwargs['height']
    else:
        raise ValueError("Unsupported shape")

def perimeter(shape, **kwargs):
    if shape == 'circle':
        return 2 * math.pi * kwargs['radius']
    elif shape == 'rectangle':
        return 2 * (kwargs['length'] + kwargs['width'])
    elif shape == 'triangle':
        return kwargs['side1'] + kwargs['side2'] + kwargs['side3']
    else:
        raise ValueError("Unsupported shape")