#Efrat Sofer 304855125
import sys

def main():
    #print("Hello World!")
    try:
        #read input file
        input_file = open(sys.argv[1], 'r')
        input_lines = input_file.read().splitlines()
        att = input_lines[0].split('\t')
        att.pop()
        print("got input file")
    except(ValueError, IndexError):
        print("no input file given")



if __name__ == "__main__":
    main()