import pickle
import json
from FOON_class import Object

# -----------------------------------------------------------------------------------------------------------------------------#

# Checks an ingredient exists in kitchen


def check_if_exist_in_kitchen(kitchen_items, ingredient):
    """
        parameters: a list of all kitchen items,
                    an ingredient to be searched in the kitchen
        returns: True if ingredient exists in the kitchen
    """

    for item in kitchen_items:
        if item["label"] == ingredient.label \
                and sorted(item["states"]) == sorted(ingredient.states) \
                and sorted(item["ingredients"]) == sorted(ingredient.ingredients) \
                and item["container"] == ingredient.container:
            return True

    return False


# -----------------------------------------------------------------------------------------------------------------------------#
# Initial BFS Traversal Algorithm

def search_BFS(kitchen_items=[], goal_node=None):
    # list of indices of functional units
    reference_task_tree = []

    # list of object indices that need to be searched
    items_to_search = []

    # find the index of the goal node in object node list
    # Start the search at the goal node
    # Before exploring another node, you must confirm whether or not that item is in the kitchen
    items_to_search.append(goal_node.id)

    # list of item already explored
    items_already_searched = []

    while len(items_to_search) > 0:
        current_item_index = items_to_search.pop(0)  # pop the first element
        if current_item_index in items_already_searched:
            continue

        else:
            items_already_searched.append(current_item_index)

        current_item = foon_object_nodes[current_item_index]

        # If the item is not available in the kitchen, then the node must be registered as explored
        # If the item is available in the kitchen, there is no need to explore the node
        if not check_if_exist_in_kitchen(kitchen_items, current_item):

            candidate_units = foon_object_to_FU_map[current_item_index]

            # In this particular function without using heuristics, the first example of a particular item in a particular state is selected
            # With a heuristic algorithm factored in, you choose an item with a particular criteria in mind rather than simply the first item in the list
            selected_candidate_idx = candidate_units[0]

            # if an fu is already taken, do not process it again
            if selected_candidate_idx in reference_task_tree:
                continue

            reference_task_tree.append(selected_candidate_idx)

            # all input of the selected FU need to be explored
            for node in foon_functional_units[
                    selected_candidate_idx].input_nodes:
                node_idx = node.id

                # Do not touch this if statement
                if node_idx not in items_to_search:

                    # if in the input nodes, we have bowl contains {onion} and onion, chopped, in [bowl]
                    # explore only onion, chopped, in bowl
                    flag = True
                    if node.label in utensils and len(node.ingredients) == 1:
                        for node2 in foon_functional_units[
                                selected_candidate_idx].input_nodes:
                            if node2.label == node.ingredients[
                                    0] and node2.container == node.label:

                                flag = False
                                break
                    if flag:
                        items_to_search.append(node_idx)

    # reverse the task tree
    reference_task_tree.reverse()

    # create a list of functional unit from the indices of reference_task_tree
    task_tree_units = []
    for i in reference_task_tree:
        task_tree_units.append(foon_functional_units[i])

    return task_tree_units


def save_paths_to_file(task_tree, path):

    print('writing generated task tree to ', path)
    _file = open(path, 'w')

    _file.write('//\n')
    for FU in task_tree:
        _file.write(FU.get_FU_as_text() + "\n")
    _file.close()

# -----------------------------------------------------------------------------------------------------------------------------#
# Iterative Deepening Search Algorithm

def search_Iter_Deep(max_depth_list=[], kitchen_items=[], goal_node=None):

    # An array of Maximum Depths to be searched is added as an input argument. If the goal node is not found in one depth, the next depth in the array is called which deepens the search.
    for max_depth in max_depth_list:
        for depth in range(max_depth):
            # list of indices of functional units
            reference_task_tree = []

            # list of object indices that need to be searched
            items_to_search = []

            # find the index of the goal node in object node list
            # Start the search at the goal node
            # Before exploring another node, you must confirm whether or not that item is in the kitchen
            items_to_search.append(goal_node.id)

            # list of item already explored
            items_already_searched = []

            while len(items_to_search) > 0:
                current_item_index = items_to_search.pop(0)  # pop the first element

                if current_item_index in items_already_searched:
                    continue
                else:
                    items_already_searched.append(current_item_index)

                current_item = foon_object_nodes[current_item_index]

                # If the item is not available in the kitchen, then the node must be registered as explored
                # If the item is available in the kitchen, there is no need to explore the node
                if not check_if_exist_in_kitchen(kitchen_items, current_item):

                    candidate_units = foon_object_to_FU_map[current_item_index]

                    # selecting the first path
                    selected_candidate_idx = candidate_units[0]

                    # if an fu is already taken, do not process it again
                    if selected_candidate_idx in reference_task_tree:
                        continue

                    reference_task_tree.append(selected_candidate_idx)

                    for node in foon_functional_units[selected_candidate_idx].input_nodes:
                        node_idx = node.id

                        # Do not touch this if statement
                        if node_idx not in items_to_search:

                            # if in the input nodes, we have bowl contains {onion} and onion, chopped, in [bowl]
                            # explore only onion, chopped, in bowl
                            flag = True
                            if node.label in utensils and len(node.ingredients) == 1:
                                for node2 in foon_functional_units[selected_candidate_idx].input_nodes:
                                    if node2.label == node.ingredients[0] and node2.container == node.label:
                                        flag = False
                                        break
                            if flag:
                                items_to_search.append(node_idx)
            
                    
            # If goal node is found, create and return the task tree units array
            if goal_node.id in items_already_searched:

                # reverse the task tree
                reference_task_tree.reverse()

                # create a list of functional unit from the indices of reference_task_tree
                task_tree_units = []
                for i in reference_task_tree:
                    task_tree_units.append(foon_functional_units[i])

                return task_tree_units
    
            # If goal node isn't found, return false
            return False


# -----------------------------------------------------------------------------------------------------------------------------#
# Greedy Best-First Search Algorithm - Maximized Success Rate of Motion

def search_Greedy_BFS_SuccessRate(kitchen_items=[], goal_node=None):
    # list of indices of functional units
    reference_task_tree = []

    # list of object indices that need to be searched
    items_to_search = []

    # find the index of the goal node in object node list
    items_to_search.append(goal_node.id)

    # list of item already explored
    items_already_searched = []

    while len(items_to_search) > 0:
        current_item_index = items_to_search.pop(0)  # pop the first element
        if current_item_index in items_already_searched:
            continue

        else:
            items_already_searched.append(current_item_index)

        current_item = foon_object_nodes[current_item_index]

        if not check_if_exist_in_kitchen(kitchen_items, current_item):

            candidate_units = foon_object_to_FU_map[current_item_index]

            # selecting the first path
            # The selected candidate, rather than simply being the first option, needs to be the option with the motion node with the highest success rate according to the values in motion.txt
            
            # Built a dictionary from the data in motion.txt
            motion_dict = {}
            with open("motion.txt") as motion_stats:
                for line in motion_stats:
                    (key, val) = line.split("\t")
                    motion_dict[str(key)] = float(val)

            # Created 2 lists based off of the dictionary values
            motions_list = []
            eff_values_list = []

            for motion in motion_dict:
                motions_list.append(motion)
            for value in motion_dict.values():
                eff_values_list.append(value)

            # Used max_eff to store the maximum efficiency value found within the motion node lists.
            # The motion node component of each candidate in the candidate_units list is evaluated. Since both the motions list and eff_values_list are of equal length with corresponding data, they can both be traversed with a common counter variable
            max_eff = 0
            for index in candidate_units:
                counter = 0
                for motion in motions_list:
                    if foon_functional_units[index].motion_node == motion:
                        # If the maximum effieciency is greater than max_eff, max_eff is replaced with said value and the selected candidate variable is said to the index of said motion node
                        if eff_values_list[counter] > max_eff:
                            max_eff = eff_values_list[counter]
                            selected_candidate_idx = index
                            # Since the maximum possible efficiency is 0.90, there is no need to search the rest of the list if this value is reached
                            if max_eff == 0.90:
                                break
                    counter += 1
            

            # if an fu is already taken, do not process it again
            if selected_candidate_idx in reference_task_tree:
                continue

            reference_task_tree.append(selected_candidate_idx)

            # all input of the selected FU need to be explored
            for node in foon_functional_units[
                    selected_candidate_idx].input_nodes:
                # To reference the motion node, you must change input_nodes to motion_nodes
                node_idx = node.id
                if node_idx not in items_to_search:

                    # if in the input nodes, we have bowl contains {onion} and onion, chopped, in [bowl]
                    # explore only onion, chopped, in bowl
                    flag = True
                    if node.label in utensils and len(node.ingredients) == 1:
                        for node2 in foon_functional_units[
                                selected_candidate_idx].input_nodes:
                            if node2.label == node.ingredients[
                                    0] and node2.container == node.label:

                                flag = False
                                break
                    if flag:
                        items_to_search.append(node_idx)

    # reverse the task tree
    reference_task_tree.reverse()

    # create a list of functional unit from the indices of reference_task_tree
    task_tree_units = []
    for i in reference_task_tree:
        task_tree_units.append(foon_functional_units[i])

    return task_tree_units


# -----------------------------------------------------------------------------------------------------------------------------#
# Greedy Best-First Search Algorithm - Minimized Number of Input Objects

def search_Greedy_BFS_NumObjects(kitchen_items=[], goal_node=None):
    # list of indices of functional units
    reference_task_tree = []

    # list of object indices that need to be searched
    items_to_search = []

    # find the index of the goal node in object node list
    items_to_search.append(goal_node.id)

    # list of item already explored
    items_already_searched = []

    while len(items_to_search) > 0:
        current_item_index = items_to_search.pop(0)  # pop the first element
        if current_item_index in items_already_searched:
            continue

        else:
            items_already_searched.append(current_item_index)

        current_item = foon_object_nodes[current_item_index]

        if not check_if_exist_in_kitchen(kitchen_items, current_item):

            candidate_units = foon_object_to_FU_map[current_item_index]

            # selecting the first path
            # The selected candidate, rather than simply being the first option, needs to be the option with the lowest number of input objects

            # Use min_input_objects to store the minimum number of input objects discovered among the values in candidate_units, initially set to an arbitrarily large number
            min_input_objects = 9999
            for index in candidate_units:
                # Simply analyze the length of the input node array of the candidate, and keep track of the one that has the shortest array
                if len(foon_functional_units[index].input_nodes) < min_input_objects:
                    min_input_objects = len(foon_functional_units[index].input_nodes)
                    selected_candidate_idx = index
            

            # if an fu is already taken, do not process it again
            if selected_candidate_idx in reference_task_tree:
                continue

            reference_task_tree.append(selected_candidate_idx)

            # all input of the selected FU need to be explored
            for node in foon_functional_units[
                    selected_candidate_idx].input_nodes:
                node_idx = node.id
                if node_idx not in items_to_search:

                    # if in the input nodes, we have bowl contains {onion} and onion, chopped, in [bowl]
                    # explore only onion, chopped, in bowl
                    flag = True
                    if node.label in utensils and len(node.ingredients) == 1:
                        for node2 in foon_functional_units[
                                selected_candidate_idx].input_nodes:
                            if node2.label == node.ingredients[
                                    0] and node2.container == node.label:

                                flag = False
                                break
                    if flag:
                        items_to_search.append(node_idx)

    # reverse the task tree
    reference_task_tree.reverse()

    # create a list of functional unit from the indices of reference_task_tree
    task_tree_units = []
    for i in reference_task_tree:
        task_tree_units.append(foon_functional_units[i])

    return task_tree_units


# -----------------------------------------------------------------------------------------------------------------------------#

# creates the graph using adjacency list
# each object has a list of functional list where it is an output


def read_universal_foon(filepath='FOON.pkl'):
    """
        parameters: path of universal foon (pickle file)
        returns: a map. key = object, value = list of functional units
    """
    pickle_data = pickle.load(open(filepath, 'rb'))
    functional_units = pickle_data["functional_units"]
    object_nodes = pickle_data["object_nodes"]
    object_to_FU_map = pickle_data["object_to_FU_map"]

    return functional_units, object_nodes, object_to_FU_map


# -----------------------------------------------------------------------------------------------------------------------------#

if __name__ == '__main__':
    foon_functional_units, foon_object_nodes, foon_object_to_FU_map = read_universal_foon(
    )

    utensils = []
    with open('utensils.txt', 'r') as f:
        for line in f:
            utensils.append(line.rstrip())

    kitchen_items = json.load(open('kitchen.json'))

    goal_nodes = json.load(open("goal_nodes.json"))

    for node in goal_nodes:
        node_object = Object(node["label"])
        node_object.states = node["states"]
        node_object.ingredients = node["ingredients"]
        node_object.container = node["container"]

        for object in foon_object_nodes:
            if object.check_object_equal(node_object):

                # Outputs the task tree using the standard BFS algorithm
                output_task_tree_BFS = search_BFS(kitchen_items, object)
                save_paths_to_file(output_task_tree_BFS, 'output_BFS_{}.txt'.format(node["label"]))

                # Outputs the task tree using the IDFS algorithm
                # I created an array of depths to search for a solution in to be used as an input argument for the Iterative Deepening Search Function
                max_depths_array = [2, 5, 8, 11]
                output_task_tree_Iter_Deep = search_Iter_Deep(max_depths_array, kitchen_items, object)
                save_paths_to_file(output_task_tree_Iter_Deep, 'output_Iter_Deep_{}.txt'.format(node["label"]))

                # Outputs the task tree using the Greedy BFS algorithm with the heuristic based on the motion node success rate
                output_task_tree_Greedy_BFS_SuccessRate = search_Greedy_BFS_SuccessRate(kitchen_items, object)
                save_paths_to_file(output_task_tree_Greedy_BFS_SuccessRate, 'output_Greedy_BFS_SuccessRate_{}.txt'.format(node["label"]))

                # Outputs the task tree using the Greedy BFS algorithm with the heuristic based on the fewest number of input objects
                output_task_tree_Greedy_BFS_NumObjects = search_Greedy_BFS_NumObjects(kitchen_items, object)
                save_paths_to_file(output_task_tree_Greedy_BFS_NumObjects, 'output_Greedy_BFS_NumObjects_{}.txt'.format(node["label"]))

                print("END SUCCESS\n\n\n")

                break
