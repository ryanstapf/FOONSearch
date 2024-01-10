from FOON_class import FunctionalUnit, Object
import pickle

# -----------------------------------------------------------------------------------------------------------------------------#


def get_FU_list(filepath):
    """
        parameters: path of a text file
        returns: a list of FU
    """
    lines = open(filepath, 'r')

    FU_list = []

    FU = FunctionalUnit()
    new_object = None
    is_input = True

    for line in lines:

        if line.startswith("//"):
            # functional unit separators:

            # check if an object is constructed
            if new_object:
                FU.output_nodes.append(new_object)
                new_object = None
                # if FU is already constructed, add it to the FU list
            if FU.motion_node:
                FU_list.append(FU)
                FU = FunctionalUnit()

            is_input = True

            continue

        label = line.split("\t")
        if len(label) < 2:
            # -- this is to make sure that we skip incorrect lines
            print(
                ' -- WARNING: there is a line that is possibly incorrect : ' +
                str(label))
            continue

        label[1] = label[1].lower().rstrip()

        if line.startswith("O"):
            if new_object:
                # decide whether to add as input or output node
                if not is_input:
                    FU.output_nodes.append(new_object)
                else:
                    FU.input_nodes.append(new_object)

            # len = 3 for goal node
            new_object = Object(label[1])
            if len(label) > 2:
                new_object.object_in_motion = label[2]
            if len(label) > 3:
                new_object.recipe_category = label[3].rstrip()

        if line.startswith("S"):

            if len(label) > 2:
                # add the ingredients to current object
                if label[2].startswith('{'):
                    ingredients = label[2].rstrip().replace('{', '').replace(
                        '}', '')
                    new_object.ingredients = ingredients.split(',')

                # add the container to current object
                elif label[2].startswith('['):
                    container = label[2].rstrip().replace('[',
                                                          '').replace(']', '')
                    new_object.container = container

            else:
                new_object.states.append(label[1])

        if line.startswith("M"):
            # append the current object
            FU.input_nodes.append(new_object)
            new_object = None
            is_input = False
            FU.motion_node = label[1]

    return FU_list


def create_graph(foon_file='FOON.txt'):

    functional_units = []
    fu_id = 0

    FU_list = get_FU_list(foon_file)
    for FU in FU_list:
        # checking duplicate functional unit
        if not FU.check_if_FU_exist(functional_units):
            FU.id = fu_id  # set the id according to its index
            functional_units.append(FU)
            fu_id += 1

    # save universal foon in a pickle file
    object_nodes = []
    object_id = 0
    for FU in functional_units:
        for _input in FU.input_nodes:
            # avoid adding duplicate objects
            existing_object_id = _input.check_object_exist(object_nodes)

            # if the object exists, assign the existing object id
            # if it does not, give it a new id
            if existing_object_id == -1:  # object is not found
                _input.id = object_id
                object_nodes.append(_input)
                object_id += 1
            else:
                _input.id = existing_object_id

        for _output in FU.output_nodes:
            existing_object_id = _output.check_object_exist(object_nodes)

            if existing_object_id == -1:  # object is not found
                _output.id = object_id
                object_nodes.append(_output)
                object_id += 1
            else:
                _output.id = existing_object_id

    object_to_FU_map = {}

    # create a mapping between output node to functional units
    # in this map, key = object index in object_nodes,
    # value = index of all FU where this object is an output
    for FU_index, FU in enumerate(functional_units):
        for _output in FU.output_nodes:

            # ignore object that has no state like "knife"
            if len(_output.states) == 0 and len(
                    _output.ingredients) == 0 and _output.container == None:
                continue

            object_index = _output.id
            if object_index not in object_to_FU_map:
                object_to_FU_map[object_index] = []
            object_to_FU_map[object_index].append(FU_index)

    F = open('FOON.pkl', "wb")
    pickle_data = {
        "functional_units": functional_units,
        "object_nodes": object_nodes,
        "object_to_FU_map": object_to_FU_map
    }
    pickle.dump(pickle_data, F)
    F.close()
    print('-- universal foon saved to FOON.pkl')

    print('-- total functional unit:', len(functional_units))
