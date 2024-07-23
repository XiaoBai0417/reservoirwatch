import numpy as np
import cv2
import matplotlib.pyplot as plt

# Create a blank binary image
def create_blank_image(size=(200, 200)):
    """Create a blank black image."""
    return np.zeros(size, dtype=np.uint8)

# Add geometric shapes to the image
def add_shapes_to_image(image):
    """Add shapes to the image and return a list of their coordinates."""
    shapes = []
    # Add a rectangle
    rectangle = np.array([[50, 50], [100, 50], [100, 100], [50, 100]], dtype=np.int32)
    cv2.fillPoly(image, [rectangle], 255)
    shapes.append((rectangle, 'rectangle'))
    
    # Add a triangle
    triangle = np.array([[150, 50], [200, 100], [100, 100]], dtype=np.int32)
    cv2.fillPoly(image, [triangle], 255)
    shapes.append((triangle, 'triangle'))

    # Add a rectangle2
    rectangle2 = np.array([[10, 10], [20, 10], [20, 20],  [10, 20]], dtype=np.int32)
    cv2.fillPoly(image, [rectangle2], 255)
    shapes.append((rectangle2, 'rectangle2'))

    triangle2 = np.array([[150, 150], [190, 190], [100, 190]], dtype=np.int32)
    cv2.fillPoly(image, [triangle2], 255)
    shapes.append((triangle2, 'triangle2'))
    
    return shapes

# Generate a random point inside one of the shapes
def generate_point_in_shape(shapes, image):
    """Generate a random point that falls within one of the shapes."""
    mask = np.zeros(image.shape, dtype=np.uint8)
    for shape, _ in shapes:
        cv2.fillPoly(mask, [shape], 255)
    while True:
        x = np.random.randint(0, image.shape[1])
        y = np.random.randint(0, image.shape[0])
        if mask[y, x] == 255:
            return (x, y)

# Find which shape contains the given point
def find_shape_containing_point(shapes, point):
    """Determine which shape contains the given point."""
    for shape, _ in shapes:
        if cv2.pointPolygonTest(shape, point, False) >= 0:
            return shape
    return None

# Main function to run the operations
def main():
    image_size = (200, 200)
    image = create_blank_image(image_size)
    shapes = add_shapes_to_image(image)
    
    point = generate_point_in_shape(shapes, image)
    containing_shape = find_shape_containing_point(shapes, point)

    # Display the results
    plt.imshow(image, cmap='gray')
    for shape, label in shapes:
        if label == 'rectangle':
            plt.plot(shape[:,0], shape[:,1], 'r-')  # Draw rectangle in red
        elif label == 'triangle':
            plt.plot(np.append(shape[:,0], shape[0,0]), np.append(shape[:,1], shape[0,1]), 'r-')  # Draw triangle in red
    plt.plot(point[0], point[1], 'bo')  # Mark the point in blue
    plt.title(f'Point is inside a {containing_shape[1]}')
    plt.axis('off')  # Turn off axis
    plt.show()

if __name__ == '__main__':
    main()
