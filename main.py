import sqlite3
import matplotlib.pyplot as plt
import itertools

from BinaryTree import BinaryTree
from Nodes import Node, InfinityNode
from Players import Cop, Robber, InfinityCop, InfinityRobber


def setup_database():
    connection = sqlite3.connect("infinite_tree_simulation.db")
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS captures (
              id INTEGER PRIMARY KEY,
              cop_tipsiness REAL,
              robber_tipsiness REAL,
              start_distance INTEGER,
              vertex_degree INTEGER,
              num_trials INTEGER,
              simulated_capture_time REAL,
              expected_capture_time REAL
              )
    ''')
    connection.commit()
    connection.close()


def store_results(cop_tipsiness: float, robber_tipsiness: float, start_distance: int, vertex_degree: int, num_trials: int, simulated_capture_time: float, expected_capture_time: float):
    connection = sqlite3.connect("infinite_tree_simulation.db")
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO captures (cop_tipsiness, robber_tipsiness, start_distance, vertex_degree, num_trials, simulated_capture_time, expected_capture_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (cop_tipsiness, robber_tipsiness, start_distance, vertex_degree, num_trials, simulated_capture_time, expected_capture_time))

    connection.commit()
    connection.close()


def play_finite_game(cop_node: Node, robber_node: Node, cop_tipsiness: float = 0, robber_tipsiness: float = 0, num_times: int = 1):
    cop = Cop(cop_node, cop_tipsiness)
    robber = Robber(robber_node, robber_tipsiness)

    total_cop_moves = 0
    total_robber_moves = 0

    for i in range(num_times):
        cop.set_node(cop_node)
        robber.set_node(robber_node)

        cop_moves = 0
        robber_moves = 0

        caught = False
        while not caught:
            caught = cop.greedy_move(robber.get_node())
            cop_moves += 1
            if caught:
                break
            caught = robber.greedy_move(cop.get_node())
            robber_moves += 1
        
        total_cop_moves += cop_moves
        total_robber_moves += robber_moves

    print()
    print(f"cop tipsiness: {cop_tipsiness}, rob tipsiness: {robber_tipsiness}")
    print()
    print(f"total_cop_moves: {total_cop_moves}")
    print()
    print(f"average cop moves: {total_cop_moves / num_times}")
    print(f"average robber moves: {total_cop_moves / num_times}")


def play_infinite_game(start_distance: int = 2, cop_tipsiness: float = 0, robber_tipsiness: float = 0, min_degree: int = 3, max_degree: int = 3, num_times: int = 1, print_individual: bool = True):
    if cop_tipsiness == 0:
        if start_distance % 2 == 0:
            expected_average = start_distance * min_degree / (2 * robber_tipsiness)
            if print_individual:
                print(f"sr/2x_r = {expected_average}")
        else:
            expected_average = (start_distance - 1) * min_degree / (2 * robber_tipsiness) + 1
            if print_individual:
                print(f"(s-1)r/2x_r + 1 = {expected_average}")
    else:
        if start_distance % 2 == 0:
            expected_average = start_distance / (2 * ((cop_tipsiness + robber_tipsiness) / min_degree - cop_tipsiness))
            if print_individual:
                print(f"s/(2((x_c+x_r)/r)) = {expected_average}")
        else:
            expected_average = (start_distance - 1) / (2 * ((cop_tipsiness + robber_tipsiness) / min_degree - cop_tipsiness)) + 1
            if print_individual:
                print(f"(s-1)/(2((x_c+x_r)/r-x_c)) + 1 = {expected_average}")


    cop_start_node = InfinityNode(None, min_degree, max_degree)
    robber_start_node = cop_start_node

    for i in range(start_distance):
        robber_start_node = robber_start_node.get_neighbours()[-1]
        robber_start_node.visit()
    
    cop = InfinityCop(cop_start_node, cop_tipsiness)
    robber = InfinityRobber(robber_start_node, robber_tipsiness)

    total_cop_moves = 0
    total_robber_moves = 0

    for i in range(num_times):
        cop.set_node(cop_start_node)
        robber.set_node(robber_start_node)

        cop_moves = 0
        robber_moves = 0

        caught = False

        while not caught:
            caught = cop.greedy_move(robber.get_node())
            cop_moves += 1
            if caught:
                break
            caught = robber.greedy_move(cop.get_node())
            robber_moves += 1
        
        total_cop_moves += cop_moves
        total_robber_moves += robber_moves
    
    average_cop_moves = total_cop_moves / num_times

    if print_individual:
        print()
        print(f"cop tipsiness: {cop_tipsiness}, robber tipsiness: {robber_tipsiness}")
        print()
        print(f"total cop moves: {total_cop_moves}")
        print()
        print(f"average cop moves: {average_cop_moves}")
        print("-------------------------------------------------------------")

    store_results(cop_tipsiness, robber_tipsiness, start_distance, min_degree, num_times, average_cop_moves, expected_average)


def show_comparison(cop_tipsiness: float = 0):
    connection = sqlite3.connect("infinite_tree_simulation.db")
    cursor = connection.cursor()
    cursor.execute('''
                   SELECT DISTINCT start_distance FROM captures
    ''')

    start_distances = cursor.fetchall()

    values = []

    for start_distance in start_distances:
        cursor.execute('''
                    SELECT simulated_capture_time
                       FROM captures
                       WHERE start_distance = ? AND cop_tipsiness = ?
                       ORDER BY robber_tipsiness
        ''', ((start_distance[0], cop_tipsiness)))

        simulated_time = cursor.fetchall()
        values.append((f"s = {start_distance[0]}, simulated", simulated_time))

        cursor.execute('''
                    SELECT expected_capture_time
                       FROM captures
                       WHERE start_distance = ? AND cop_tipsiness = ?
                       ORDER BY robber_tipsiness
        ''', ((start_distance[0], cop_tipsiness)))

        expected_time = cursor.fetchall()
        values.append((f"s = {start_distance[0]}, expected", expected_time))
    
    cursor.execute('''
                SELECT DISTINCT robber_tipsiness
                    FROM captures
    ''')
    categories = list(itertools.chain(*cursor.fetchall()))

    is_simulated = True

    for dataset in values:
        name = dataset[0]
        data = list(itertools.chain(*dataset[1]))
        marker = "o" if is_simulated else "s"
        is_simulated = not is_simulated

        if len(data) == len(categories):
            plt.plot(categories, data, marker = marker, label = name)

    plt.title(f"Comparison of Expected Capture Time Vs Simulated Capture Time With\nCop Tipsiness of {cop_tipsiness}")
    plt.xlabel("Robber tipsiness")
    plt.ylabel("Number of Cop Moves")
    plt.legend()
    plt.grid(True)

    plt.show()

    cursor.close()



def show_difference(cop_tipsiness: float = 0):
    connection = sqlite3.connect("infinite_tree_simulation.db")
    cursor = connection.cursor()

    cursor.execute('''
                   SELECT DISTINCT start_distance FROM captures
    ''')

    start_distances = cursor.fetchall()

    values = []

    for start_distance in start_distances:
        cursor.execute('''
                        SELECT 
                            CASE 
                                WHEN expected_capture_time > simulated_capture_time THEN expected_capture_time - simulated_capture_time
                                ELSE simulated_capture_time - expected_capture_time
                            END
                        FROM captures
                        WHERE start_distance = ? AND cop_tipsiness = ?
        ''', ((start_distance[0], cop_tipsiness)))
        
        values.append((f"s = {start_distance[0]}", cursor.fetchall()))

    cursor.execute('''
                SELECT DISTINCT robber_tipsiness
                    FROM captures
    ''')
    categories = list(itertools.chain(*cursor.fetchall()))

    for dataset in values:
        name = dataset[0]
        data = list(itertools.chain(*dataset[1]))
        if len(data) == len(categories):
            plt.plot(categories, data, marker = "o", label = name)
    
    plt.title(f"Difference Between Expected and Simulated Capture Times With\nCop Tipsiness of {cop_tipsiness}")
    plt.xlabel("Robber Tipsiness")
    plt.ylabel("Difference")
    plt.legend()
    plt.grid(True)

    plt.show()


'''
Infinite Game Simulation
'''

# start_distance = 3

# cop_tipsiness = 0
# robber_tipsiness = 0.1

# # Database and calculations don't support different degrees.
# min_degree = max_degree = 3

# num_times = 50000

# print_individual = False


# for start_distance in range(2, 7, 2):
#     for j in range(0, 5):
#         cop_tipsiness = j / 100
#         for i in range(1, 11):
#             robber_tipsiness = i / 10
#             print(f"Processing s={start_distance}, cop={cop_tipsiness}, robber={robber_tipsiness}")
#             play_infinite_game(start_distance, cop_tipsiness, robber_tipsiness, min_degree, max_degree, num_times, print_individual)
#             print(f"Finished s={start_distance}, cop={cop_tipsiness}, robber={robber_tipsiness}")
#             print()


'''
Finite Game Simulation
'''

# tree_height = 3
# tree_density = 0.6

# bin_tree = BinaryTree(tree_height, tree_density)
# bin_tree.visualize()

# cop_node = bin_tree.get_root()
# robber_node = bin_tree.get_root().get_l_child().get_l_child()

# cop_tipsiness = 0.6
# robber_tipsiness = 0

# num_trials = 50000

# play_finite_game(bin_tree.get_root(), bin_tree.get_root().get_l_child().get_l_child(), cop_tipsiness, robber_tipsiness, num_trials)


'''
Database
'''
setup_database()

show_comparison(0.04)
# show_difference(0.02)