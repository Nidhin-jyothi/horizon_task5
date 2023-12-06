import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from PIL import Image

class Graph:
    def __init__(self):
        self.points = []
        self.adjacency_matrix = []

    def add_point(self, x, y):
        self.points.append((x, y))
        self.update_adjacency_matrix()

    def update_adjacency_matrix(self):
        num_points = len(self.points)
        self.adjacency_matrix = [[0] * num_points for _ in range(num_points)]

        for i in range(num_points):
            for j in range(i + 1, num_points):
                distance = self.calculate_distance(self.points[i], self.points[j])
                self.adjacency_matrix[i][j] = self.adjacency_matrix[j][i] = distance

    @staticmethod
    def calculate_distance(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])  # Manhattan distance

    def display_adjacency_matrix(self):
        for row in self.adjacency_matrix:
            print("\t".join(map(str, row)))

    def predict_shortest_path(self):
        # Implement logic to predict the shortest path using Dijkstra's algorithm
        print("Functionality not implemented yet.")

class ImageClick:
    def __init__(self, image_path, reference_coordinates):
        self.image_path = image_path
        self.reference_coordinates = reference_coordinates
        try:
            self.img = Image.open(image_path)
        except Exception as e:
            print(f"Error opening the image: {e}")
            return

        self.fig, self.ax = plt.subplots()
        self.ax.imshow(self.img)

        self.coordinates = []

        self.cursor = Cursor(self.ax, useblit=True, color='red', linewidth=1)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        # Adjust aspect ratio and set axis limits
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.set_xlim(0, self.img.width)
        self.ax.set_ylim(self.img.height, 0)

        plt.show()

    def on_click(self, event):
        if event.inaxes == self.ax:
            x, y = int(event.xdata), int(event.ydata)
            self.coordinates.append((x, y))
            print(f"Clicked at coordinates: ({x}, {y})")

def upload_image_and_coordinates(graph):
    try:
        num_coordinates = 4
        for i in range(num_coordinates):
            x = int(input(f"Enter x-coordinate for point {i + 1}: "))
            y = int(input(f"Enter y-coordinate for point {i + 1}: "))
            graph.add_point(x, y)

        print("Coordinates uploaded successfully.")
    except ValueError:
        print("Invalid input. Please enter numerical values for coordinates.")

def select_points(graph):
    if not graph.points:
        print("Please upload coordinates first (Menu option 1).")
    else:
        image_path = input("Enter the path of the image: ")
        image_click = ImageClick(image_path, graph.points)
        # Save the clicked coordinates for later use if needed
        clicked_coordinates = image_click.coordinates
        print("Coordinates clicked on the image:")
        for i, (x, y) in enumerate(clicked_coordinates, start=1):
            print(f"Point {i}: ({x}, {y})")

def predict_shortest_path(graph):
    graph.predict_shortest_path()

# Create an empty graph
graph = Graph()

while True:
    print("\nMenu:")
    print("1. Upload Image and Enter Coordinates")
    print("2. Select Points")
    print("3. Predict Shortest Path")
    print("4. Exit")

    choice = input("Enter your choice (1-4): ")

    if choice == "1":
        upload_image_and_coordinates(graph)
    elif choice == "2":
        select_points(graph)
    elif choice == "3":
        predict_shortest_path(graph)
    elif choice == "4":
        print("Exiting the program. Goodbye!")
        break
    else:
        print("Invalid choice. Please enter a valid option.")
