import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from PIL import Image
from itertools import combinations
import heapq
import networkx as nx
import matplotlib.pyplot as plt
import csv
import os
import ast
import itertools

image_path=""




class Node:
    def __init__(self, point):
        self.point = point
        self.neighbors = []

    def add_neighbor(self, neighbor, difficulty):
        self.neighbors.append((neighbor, difficulty))

class WeightedGraph:
    def __init__(self):
        self.points = {}
        self.G = nx.Graph()

    def add_point(self, point):
        new_point = Node(point)
        self.points[point] = new_point
        self.G.add_node(point)

    def add_path(self, source, destination, difficulty):
        if source not in self.points:
            self.add_point(source)
        if destination not in self.points:
            self.add_point(destination)

        if isinstance(difficulty, (int, float)):
            self.points[source].add_neighbor(self.points[destination], difficulty)
            self.points[destination].add_neighbor(self.points[source], difficulty)
            self.G.add_edge(source, destination, weight=difficulty)
        else:
            print("Invalid difficulty level. Please enter a valid number.")

    def dijkstra(self, start):
        difficulties = {point: float('infinity') for point in self.points}
        previous_points = {point: None for point in self.points}
        difficulties[start] = 0
        priority_queue = [(0, start)]

        while priority_queue:
            current_difficulty, current_point = heapq.heappop(priority_queue)
            if current_difficulty > difficulties[current_point]:
                continue

            for neighbor, difficulty in self.points[current_point].neighbors:
                path_difficulty = current_difficulty + difficulty
                if path_difficulty < difficulties[neighbor.point]:
                    difficulties[neighbor.point] = path_difficulty
                    previous_points[neighbor.point] = current_point
                    heapq.heappush(priority_queue, (path_difficulty, neighbor.point))

        return difficulties, previous_points

    def reroute_from_new_node(self, traveled_path, new_current_node, end_node):
        new_path = self.best_path(new_current_node, end_node)
        if new_path:
            if traveled_path[-1] == new_path[0]:
                new_path = new_path[1:]
            combined_path = traveled_path + new_path
            new_distance = self.find_shortest_distance(new_current_node, end_node)
            return combined_path, new_distance
        else:
            return traveled_path, None

    def best_path(self, start, end):
        difficulties, previous_points = self.dijkstra(start)
        path = []
        current_point = end

        while current_point is not None:
            path.insert(0, current_point)
            current_point = previous_points[current_point]

        if difficulties[end] != float('infinity'):
            return path
        else:
            return []

    def find_shortest_distance(self, start, end):
        difficulties, _ = self.dijkstra(start)
        return difficulties[end]

    def visualize_graph_on_image(self, named_points, highlight_path=None):
             # Load the image
        img = Image.open(image_path)

        # Create a figure and axis for plotting
        fig, ax = plt.subplots()

        # Iterate over nodes to plot them
        for point in self.points:
            x, y = named_points[point]
            plt.scatter(x, y, label=point)

        # Draw edges
        pos = {point: (named_points[point][0], named_points[point][1]) for point in self.points}
        nx.draw_networkx_edges(self.G, pos=pos, edgelist=self.G.edges(data=True), width=1, edge_color='gray')

        # Highlight the specified path if provided
        if highlight_path:
            edges = [(highlight_path[i], highlight_path[i + 1]) for i in range(len(highlight_path) - 1)]
            nx.draw_networkx_edges(self.G, pos=pos, edgelist=edges, edge_color='red', width=2)

        # Draw labels
        nx.draw_networkx_labels(self.G, pos=pos, labels={point: point for point in self.points})

        # Show the image with nodes and edges
        ax.imshow(img)
        plt.show()

    def add_path_to_csv(self, csv_file, source, destination, time, list):
        header_exists = os.path.isfile(csv_file)
        with open(csv_file, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            if not header_exists:
                csv_writer.writerow(['Source', 'Destination', 'Time', 'Path'])
            csv_writer.writerow([source, destination, time,list])

    def load_data_from_csv(self, csv_file):
        if not os.path.isfile(csv_file):
            print("CSV file not found.")
            return

        with open(csv_file, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            for row in csv_reader:
                source, destination, time = row
                if time.replace('.', '', 1).isdigit():
                    time = float(time)
                    self.add_path(source, destination, time)
                else:
                    print(f"Invalid time value in CSV: {time}")

    def traveling_salesman_fixed_start_end(self, start, end):
        nodes = list(self.points.keys())
        nodes.remove(start)
        nodes.remove(end)

        all_paths = list(itertools.permutations(nodes))
        shortest_path = None
        shortest_distance = float('inf')

        for path in all_paths:
            total_distance = 0
            current_path = [start] + list(path) + [end]

            for i in range(len(current_path) - 1):
                total_distance += self.find_shortest_distance(current_path[i], current_path[i + 1])

            if total_distance < shortest_distance:
                shortest_distance = total_distance
                shortest_path = current_path

        return shortest_path, shortest_distance


    def travel(self, source, destination, time1, csv_file):
        closest_time = None
        chosen_path = None

        with open(csv_file, mode='r') as file:
            csv_reader = csv.reader(file)
            closest_time_diff = float('inf')

            for row in csv_reader:
                s, d, t, path_str = row
                if s == source and d == destination:
                    time_diff = abs(float(t) - float(time1))
                    if time_diff < closest_time_diff:
                        closest_time_diff = time_diff
                        closest_time = float(t)
                        chosen_path = ast.literal_eval(path_str)


        self.visualize_graph(highlight_path=chosen_path)
                # Current node checker and rerouter
        travelled_path = []
        current_node = source  # Initialize the current node with the source
        print("No matching path found in CSV. Calculating best path...")
        
        print(chosen_path)
        if not chosen_path:
            chosen_path = self.best_path(source, destination)
            print(f"No path found from {source} to {destination}.")
            # Current node checker and rerouter
            travelled_path = []
            current_node = source  # Initialize the current node with the source
            while current_node != 'done':
                print(f"Current node: {current_node}")
                print(travelled_path)
                # Display adjacent nodes to the current node
                adjacent_nodes = [neighbor[0].point for neighbor in self.points[current_node].neighbors]
                print(f"Adjacent nodes: {', '.join(adjacent_nodes)}")
                next_node = input("Enter the next node or 'done' if you have reached the destination: ").strip()
                if next_node == 'done':
                    current_node = next_node
                    break
                if next_node in adjacent_nodes or next_node == current_node:  # Check if the next node is adjacent
                    print("Valid adjacent node.")
                    travelled_path.append(next_node)
                    new_route_and_distance = self.reroute_from_new_node(travelled_path, next_node, destination)

                    if new_route_and_distance:
                        new_path, _ = new_route_and_distance  # Separate the path and distance
                        if new_path and isinstance(new_path, list):
                            print(f"New route: {' -> '.join(new_path)}")
                            self.visualize_graph(highlight_path=new_path)
                            chosen_path = new_path
                        else:
                            print("Received an invalid path from reroute_from_new_node.")
                            return None
                    else:
                        print("Invalid path. Cannot reroute to the specified node.")

                else:
                    print("Entered node is not adjacent to the current node. Please enter a valid adjacent node.")
                    continue  # Prompt for input again without changing the current node

                current_node = next_node
        if chosen_path:
            self.visualize_graph(highlight_path=chosen_path)

            # Current node checker and rerouter
            travelled_path = []
            current_node = source  # Initialize the current node with the source
            while current_node != 'done':
                print(f"Current node: {current_node}")
                # Display adjacent nodes to the current node
                adjacent_nodes = [neighbor[0].point for neighbor in self.points[current_node].neighbors]
                print(f"Adjacent nodes: {', '.join(adjacent_nodes)}")
                print("Decided path :",chosen_path)
                next_node = input("Enter the next node or 'done' if you have reached the destination: ").strip()
                if next_node == 'done':
                    current_node = next_node
                    break
                if next_node == current_node:  # Check if the next node is adjacent
                    print("Valid adjacent node.")


                else:
                    print("Intiating reouting ...")
                    status=1
                    while current_node != 'done':
                        print(f"Current node: {current_node}")
                        # Display adjacent nodes to the current node
                        adjacent_nodes = [neighbor[0].point for neighbor in self.points[current_node].neighbors]
                        print(f"Adjacent nodes: {', '.join(adjacent_nodes)}")
                        print("Decided path :",chosen_path)
                        if status==1:
                            next_node=current_node
                            status=0
                        else:
                            next_node = input("Enter the next node or 'done' if you have reached the destination: ").strip()
                        if next_node == 'done':
                            current_node = next_node
                            break
                        if next_node in adjacent_nodes or next_node == current_node:  # Check if the next node is adjacent
                            print("Valid adjacent node.")
                            travelled_path.append(next_node)
                            new_route_and_distance = self.reroute_from_new_node(travelled_path, next_node, destination)

                            if new_route_and_distance:
                                new_path, _ = new_route_and_distance  # Separate the path and distance
                                if new_path and isinstance(new_path, list):
                                    print(f"New route: {' -> '.join(new_path)}")
                                    self.visualize_graph(highlight_path=new_path)
                                    chosen_path = new_path
                                else:
                                    print("Received an invalid path from reroute_from_new_node.")
                                    return None
                            else:
                                print("Invalid path. Cannot reroute to the specified node.")

                        else:
                            print("Entered node is not adjacent to the current node. Please enter a valid adjacent node.")
                            continue  # Prompt for input again without changing the current node

                        current_node = next_node
                    break
                current_node = next_node

        # Storing the final path to CSV after reaching the destination
        if current_node == 'done':
            self.add_path_to_csv(csv_file, source, destination, time1, chosen_path)
            print("Final path details stored to CSV.")
            return chosen_path







weighted_graph = WeightedGraph()


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
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])  

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
        self.ax.set_xlim(self.img.width, 0)
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
        w = int(input(f"Enter width: "))
        h = int(input(f"Enter height: "))
        
        graph.add_point(0, 0)
        graph.add_point(w, 0)
        graph.add_point(w, h)
        graph.add_point(0, h)

        print("Coordinates uploaded successfully.")
    except ValueError:
        print("Invalid input. Please enter numerical values for coordinates.")

def select_points(graph):
    if not graph.points:
        print("Please upload coordinates first (Menu option 1).")
    else:
        global image_path
        image_path = input("Enter the path of the image: ")
        image_click = ImageClick(image_path, graph.points)
        # Save the clicked coordinates for later use if needed
        clicked_coordinates = image_click.coordinates
        print("Coordinates clicked on the image:")
        for i, (x, y) in enumerate(clicked_coordinates, start=1):
            print(f"Point {i}: ({x}, {y})")

        # Name the points
        point_names = [chr(ord('a') + i) for i in range(len(clicked_coordinates))]
        named_points = dict(zip(point_names, clicked_coordinates))

        # Calculate distances between points
        for (point1, coord1), (point2, coord2) in combinations(named_points.items(), 2):
            distance = Graph.calculate_distance(coord1, coord2)
            print(f"Distance between {point1} and {point2}: {distance}")

        # Pass the named points to the second program
        weighted_graph = integrate_with_second_program(named_points)

def integrate_with_second_program(named_points):


    
    for node, coordinates in named_points.items():
        weighted_graph.add_point(node)
        print(f"Node '{node}' added.")

    # Calculate distances between nodes and add edges to the graph
    for (node1, coord1), (node2, coord2) in combinations(named_points.items(), 2):
        distance = Graph.calculate_distance(coord1, coord2)
        weighted_graph.add_path(node1, node2, distance)

    # Visualize the graph
    weighted_graph.visualize_graph_on_image(named_points=named_points)

    start_node = input("Enter the fixed start node: ")
    end_node = input("Enter the fixed end node: ")
    shortest_path, shortest_distance = weighted_graph.traveling_salesman_fixed_start_end(start_node, end_node)
    
    if shortest_path:
        print(f"Shortest path covering all nodes with fixed start '{start_node}' and end '{end_node}': {' -> '.join(shortest_path)}")
        print(f"Total distance: {shortest_distance}")

        weighted_graph.visualize_graph_on_image(named_points=named_points,highlight_path=shortest_path)

    else:
        print("No valid path found.")

# Create an empty graph
graph1 = Graph()

while True:
    print("\nMenu:")
    print("1. Upload Image and Enter Coordinates")
    print("2. Select Points")
    print("3. Predict Shortest Path")
    print("4. Exit")

    choice = input("Enter your choice (1-4): ")

    if choice == "1":
        upload_image_and_coordinates(graph1)
    elif choice == "2":
        select_points(graph1)
    elif choice == "3":
        graph1.predict_shortest_path()
    elif choice == "4":
        print("Exiting the program.")
        break
    else:
        print("Invalid choice. Please enter a valid option.")
