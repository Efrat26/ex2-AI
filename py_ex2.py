#Efrat Sofer 304855125
import sys
import math
from collections import defaultdict


class Node:
    def __init__(self):
        self.child = []
        self.value = None
        self.decision = None

    def addChild(self, c):
        self.child.append(c)

    def setValue(self, v):
        self.value = v

    def setDecision(self, d):
        self.decision = d


'''
main function: gets the name of the input file- if not received then print error and return.
o.w continues to build the DTL tree
'''
def main():
    try:
        #read input file
        input_file = open(sys.argv[1], 'r')
        print("got input file")
    except(ValueError, IndexError):
        print("no input file given")
        return
    possible_att_values = {}
    classification_options_count = {}
    att_to_index = {}
    counter = 0
    line_sep = '\t'
    input_lines = input_file.read().splitlines()
    att = input_lines[0].split(line_sep)
    att.pop()#remove last attribute which is the classification
    #initialize dictionary keys with an empty set
    for attribute in att:
        possible_att_values[attribute] = set()
        att_to_index[attribute] = counter
        counter += 1
    #find possible values for each attribute
    for i in range(1, len(input_lines)):
        splitted_line = input_lines[i].split(line_sep)
        for j in range(0, len(att)):
            possible_att_values[att[j]].add(splitted_line[j])
        if splitted_line[-1] in classification_options_count:
            classification_options_count[splitted_line[-1]] += 1
        else:
            classification_options_count[splitted_line[-1]] = 0
    print("finished iterating the examples and finding the possible values of attributes, starting creating tree")
    input_lines_copy = input_lines.copy()
    input_lines_copy.pop(0)
    root = Node()
    DTL(input_lines_copy, list(possible_att_values.keys()), False, possible_att_values, root, att_to_index)

    #get KNN predictions values
    try:
        #read input file
        test_file_name = sys.argv[2]
        print("got test file")
    except(ValueError, IndexError):
        print("no test file given")
        test_file_name = 'test.txt'
    test_file = open(test_file_name, 'r')
    test_lines = test_file.read().splitlines()
    #get true answers
    true_answers = getAnswersVector(test_lines)
    knn_pred = KNN(5, test_lines, input_lines)
    calculateAccuracy(knn_pred, true_answers, "KNN")
    #get naive bayes classification
    nb_pred = naiveBayes(input_lines, test_lines, possible_att_values, classification_options_count)
    calculateAccuracy(nb_pred, true_answers, "naive base")


def DTL(examples, attributes, def_ret_val, possible_att_values, root_node, att_to_index_dict):
    if len(examples) == 0:
        return def_ret_val
    examples_has_same_val = checkExamplesAnswer(examples)
    if examples_has_same_val[0]:
        return examples_has_same_val[1]
    elif len(attributes) == 0:
        return examples_has_same_val[1]
    else:
        best_att = chooseBestAttribute(examples, attributes, possible_att_values, att_to_index_dict)
        print("chose best attribute: " + best_att)
        att_vals = possible_att_values[best_att]
        root_node.setValue(best_att)
        for value in att_vals:
            sub_examples = selectExamplesWithAttVal(examples, best_att, value, att_to_index_dict)
            #node for the value
            new_root_node_value = Node()
            new_root_node_value.setValue(value)
            #node for sub tree
            sub_tree_node = Node()
            print("getting subtree of attribute value:  " + value)
            attributes_copy = attributes.copy()
            attributes_copy.remove(best_att)
            ret_value = DTL(sub_examples, attributes_copy, examples_has_same_val[1], possible_att_values, sub_tree_node,
                att_to_index_dict)
            #if ret_value == True or ret_value == False:
            sub_tree_node.decision = ret_value
            new_root_node_value.addChild(sub_tree_node)
            root_node.addChild(new_root_node_value)

        #print("returning subtree")


''' 
counts the number of votes for each answer. at the end check if the dictionary has only one key (means all answers are
the same)- if so returns [True , answer]. o.w checks what is the answer of the majority and returns
 [True , majority_answer]
'''
def checkExamplesAnswer(examples):
    line_sep = '\t'
    counter_for_answer = {}
    majority_val = 0
    majority_ans = None
    for i in range(0, len(examples)):#first line has the attributes names
        splitted_line = examples[i].split(line_sep)
        answer = splitted_line[-1]
        if answer not in counter_for_answer:
            counter_for_answer[answer] = 1
        else:
            counter_for_answer[answer] += 1
    if len(counter_for_answer) == 1:
        return [True, answer]
    else:
        for key in counter_for_answer:
            if counter_for_answer[key] > majority_val:
                majority_val = counter_for_answer[key]
                majority_ans = key
        return [False, majority_ans]


def chooseBestAttribute(examples, attributes, att_vals_dict, att_to_index_dict):
    IG_val = None
    best_att = None
    for att in attributes:
        result = informationGain(examples, att, att_vals_dict[att], att_to_index_dict)
        if IG_val == None or result > IG_val:
            IG_val = result
            best_att = att
    return best_att


    print("in chooseBestAttribute")

def entropy(examples):
    line_sep = '\t'
    counter_for_answer = {}
    total_examples = len(examples)
    result = 0
    for i in range(0, len(examples)):
        splitted_line = examples[i].split(line_sep)
        answer = splitted_line[-1]
        if answer not in counter_for_answer:
            counter_for_answer[answer] = 1
        else:
            counter_for_answer[answer] += 1
    for key in counter_for_answer:
        counter_for_answer[key] = float(counter_for_answer[key])/float(total_examples)
    for key in counter_for_answer:
        result += -1*(counter_for_answer[key])*math.log2(counter_for_answer[key])
    return result


def selectExamplesWithAttVal(examples, att, att_val,att_to_index_dict):
    line_sep = '\t'
    result = []
    att_index = att_to_index_dict[att]
    for example in examples:
        splitted_example = example.split(line_sep)
        if splitted_example[att_index] == att_val:
            result.append(example)
    return result



def informationGain(examples, specific_att, att_vals, att_to_index_dict):
    entropy_data = entropy(examples)
    total_val = entropy_data
    #possible_values = att_vals[specific_att]
    for value in att_vals:
        sub_examples = selectExamplesWithAttVal(examples, specific_att, value, att_to_index_dict)
        att_val_ent = entropy(sub_examples)
        total_val -= (len(sub_examples)/len(examples))*att_val_ent
    return total_val


def hammingDist(line1, line2):
    line_sep = '\t'
    dist = 0
    splitted_line1 = line1.split(line_sep)
    splitted_line2 = line2.split(line_sep)
    for i in range(0, len(splitted_line1) - 1):#last value is the classification
        if splitted_line1[i] != splitted_line2[i]:
            dist += 1
    return dist

def KNN(number_of_neighbors, test_data, input_data):
    result_classification = []
    split_char = '\t'
    for i in range(1, len(test_data)):
        hamming_dist = []
        ind = []
        classifications = []
        for j in range(1, len(input_data)): #first line is the classification
            distance = hammingDist(test_data[i], input_data[j])
            hamming_dist.append(distance)
            ind.append(j)

        #select top neighbors
        for k in range(0, number_of_neighbors):
            min_ind = hamming_dist.index(min(hamming_dist))
            min_ind_index_in_input = ind[min_ind]
            selected_line = input_data[min_ind_index_in_input]
            splitted_line = selected_line.split(split_char)
            classifications.append(splitted_line[-1])
            hamming_dist.pop(min_ind)
            ind.pop(min_ind)
        #select majority answer
        threshold = float(number_of_neighbors)/2.0
        answer = classifications[0]
        counter_answer = 1
        other_answer = None
        for k in range(1, len(classifications)):
            if classifications[k] == answer:
                counter_answer += 1
            else:
                other_answer = classifications[k]
        if counter_answer > threshold:
            result_classification.append(answer)
        else:
            result_classification.append(other_answer)

    return result_classification



def naiveBayes(input_lines, result_lines, att_dict, classification_opt_count_dict):
    line_sep = '\t'
    result_classifications = []
    count_dict = preprocessNaiveBayse(input_lines)
    total_examples = len(input_lines) - 1
    #map index to attribute name:
    index_to_att = {}
    splitted_line = input_lines[0].split(line_sep)
    for i in range(0, len(splitted_line) -1):
        index_to_att[i] = splitted_line[i]
    # for each test line find the probability
    for i in range(1, len(result_lines)):  # first line doesn't count
        splitted_line = result_lines[i].split(line_sep)
        class_results = []
        c = []
        for classification in classification_opt_count_dict:
            result_mult = 1
            classification = classification.lower()
            for j in range(0, len(splitted_line)-1):
                conditioned_key = splitted_line[j] + '|' + classification
                att_name = index_to_att[j]
                temp = float((count_dict[conditioned_key] + 1)) / float((count_dict[classification] + len(att_dict[att_name])))#with smoothing
                #temp = float((count_dict[conditioned_key])) / float((count_dict[classification]))#without smoothing
                if temp == 0:
                    continue
                result_mult *= temp
            p_c = float(count_dict[classification]) / float(total_examples)
            result = result_mult*p_c
            class_results.append(result)
            c.append(classification)
        #find max classification
        max_ind = class_results.index(max(class_results))
        result_classifications.append(c[max_ind])
    return result_classifications

def preprocessNaiveBayse(input_lines):
    result_dict = defaultdict(int)
    split_char = '\t'
    for i in range(1, len(input_lines)):
        splitted_line = input_lines[i].split(split_char)
        for j in range(0, len(splitted_line)):
            result_dict[splitted_line[j]] += 1
            if j < len(splitted_line)-1:
                condioned_key = splitted_line[j] + "|" + splitted_line[-1].lower()
                result_dict[condioned_key] += 1
    return result_dict

def calculateAccuracy(predicted_results, true_result, method):
    if len(predicted_results) != len(true_result):
        print("result vectors aren't the same length!")
        return
    correct_ans = 0
    for i in range(0, len(predicted_results)):
        if predicted_results[i] == true_result[i]:
            correct_ans += 1
    accuracy = (float(correct_ans) / float(len(predicted_results)))*100
    print("accuracy percentage for method " + method + " is: " + str(accuracy))
    return

def getAnswersVector(lines):
    line_sep = '\t'
    result = []
    for i in range(1, len(lines)):
        splitted_line = lines[i].split('\t')
        result.append(splitted_line[-1])
    return result



if __name__ == "__main__":
    main()