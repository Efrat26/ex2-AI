#Efrat Sofer 304855125
import sys

def main():
    #print("Hello World!")
    try:
        #read input file
        input_file = open(sys.argv[1], 'r')
        print("got input file")
    except(ValueError, IndexError):
        print("no input file given")
        return
    possible_att_values = {}
    line_sep = '\t'
    input_lines = input_file.read().splitlines()
    att = input_lines[0].split(line_sep)
    att.pop()#remove last attribute which is the classification
    #initialize dictionary keys with an empty set
    for attribute in att:
        possible_att_values[attribute] = set()
    #find possible values for each attribute
    for i in range(1, len(input_lines)):
        splitted_line = input_lines[i].split(line_sep)
        for j in range(0, len(att)):
            possible_att_values[att[j]].add(splitted_line[j])
    print("finished iterating the examples and finding the possible values of attributes")

def ID3():
    print("in ID3")

def informationGain():
    print("in information gain")

def KNN(number_of_neighbors):
    print("in KNN")

def naiveBase():
    print("in naive base")

if __name__ == "__main__":
    main()