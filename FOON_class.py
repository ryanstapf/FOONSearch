class Object:
    # NOTE: -- an object node is any item that is used in the cooking/manipulation procedure.
    # 	an Object has a state type and state label to describe the state or condition it is observed in.
    # -- an Object may have multiple states! This is given by multiple lines of 'S' in the textfiles.
    """
    A object node object.

    Constructor Parameters:
            objectLabel (str): A string referring to the object's label

    """

    # NOTE: constructor for Object node:
    def __init__(self, label=None):
        # -- member variables
        self.label = label
        self.states = []
        self.ingredients = []
        self.container = None
        self.id = None  # id = index of this object in the object list

    # -- accessor methods for Objects:
    def getStateLabel(self, X):
        return self.states[X][0]

    def getObjectLabel(self):
        return self.label

    def setObjectLabel(self, L):
        self.label = L

    def setIngredients(self, L):
        self.ingredients = list(L)

    def getContainer(self, X):
        return self.states[X][1]

    # NOTE: objects can have multiple states, so we are working with a list of states:
    def getStatesList(self):
        return list(self.states)

    def getIngredients(self):
        return list(self.ingredients)

    def getIngredientsText(self):
        ingredients_list = self.getIngredients()
        ingredients = str()

        for x in range(len(ingredients_list)):
            ingredients += ingredients_list[x]
            if x < len(ingredients_list) - 1:
                ingredients += ','
            # endif
        # endfor

        return '{' + ingredients + '}'

    def addNewState(self, T):
        for S in self.states:
            # -- this is to check whether we are potentially adding a duplicate state type or label:
            if S[0] == T[0] and S[1] == T[1] and S[1]:
                print(" -- WARNING: Duplicate state detected when adding :" +
                      str(T) + " to object " + str(self.getObjectLabel()) +
                      "!")
                return
            # endif
        # endfor
        self.states.append(list(T))
        self.states.sort()

    def printObject(self):
        print("O" + "\t" + self.getObjectLabel())
        for x in range(len(self.getStatesList())):
            if "contains" in self.getStateLabel(
                    x) or "ingredients" in self.getStateLabel(x):
                print("S" + "\t" + self.getStateLabel(x) + "\t" +
                      self.getIngredientsText())
            else:
                print("S" + "\t" + self.getStateLabel(x) +
                      (str("\t " + "[" + str(self.getContainer(x)) +
                           "]") if self.getContainer(x) else ""))

    # checks if two objects are same
    def check_object_equal(self, T):
        if self.label == T.label and sorted(self.states) == sorted(T.states) \
            and sorted(self.ingredients) == sorted(T.ingredients) \
                and self.container == T.container:
            return True
        return False

    # checks if an objet exist in a list of objects
    def check_object_exist(self, object_list):
        for index, object in enumerate(object_list):
            if self.check_object_equal(object):
                return index

        return -1

    def get_object_as_json(self):
        return {
            "label": self.label,
            "states": self.states,
            "ingredients": self.ingredients,
            "container": self.container
        }

    def get_ingredients_as_text(self):
        ingredients_list = self.ingredients
        ingredients = str()

        for x in range(len(ingredients_list)):
            ingredients += ingredients_list[x]
            if x < len(ingredients_list) - 1:
                ingredients += ','
            # endif
        # endfor

        return '{' + ingredients + '}'

    def get_object_as_text(self):
        str = "O" + "\t" + self.label
        for state in self.states:
            str += "\nS" + "\t" + state
        if len(self.ingredients) > 0:
            str += '\nS' + "\t" + 'contains' + "\t" + self.get_ingredients_as_text(
            )
        if self.container:
            str += '\nS' + "\t" + 'in' + "\t" + "[" + self.container + "]"

        str += "\n"
        return str


class Motion:
    # NOTE: -- a Motion node is the other node that is found in the bipartite FOON graph.
    # -- a Motion node reflects a manipulation or non-manipulation action that is needed to change (some) objects from one state to another
    # -- a Motion node simply has a type that describes what it is along with a label.
    '''
    A motion node object.

    Constructor Parameters:
            motionID (int): An integer referring to the motion's ID
            motionLabel (str): A string referring to the motion's label
    '''

    # NOTE: constructor for Motion node:
    def __init__(self, motionLabel=None):
        # -- member variables
        self.label = motionLabel


class FunctionalUnit:

    def __init__(self):
        # NOTE: list of input and output object nodes (which use the Object class defined above):
        self.input_nodes = []
        self.output_nodes = []
        self.motion_node = None
        self.id = None  # id = index of this FU in the functional unit list

    def check_if_FU_exist(self, functional_units):

        for FU in functional_units:
            if self.motion_node != FU.motion_node or \
                len(self.input_nodes) != len(FU.input_nodes) or \
                    len(self.output_nodes) != len(FU.output_nodes):
                continue

            input_found = 0
            for node in self.input_nodes:
                if node.check_object_exist(FU.input_nodes) != -1:
                    input_found += 1

            output_found = 0
            for node in self.output_nodes:
                if node.check_object_exist(FU.output_nodes) != -1:
                    output_found += 1

            if input_found == len(self.input_nodes) and output_found == len(
                    self.output_nodes):
                return True

        return False

    def get_FU_as_text(self):
        str = ""
        for node in self.input_nodes:
            str += node.get_object_as_text()
        str += "M" + "\t" + self.motion_node + "\n"
        for node in self.output_nodes:
            str += node.get_object_as_text()
        str += "//"
        return str
