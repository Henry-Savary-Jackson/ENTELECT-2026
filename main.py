import json


car = dict()

tyres = dict()

segements = list()

current_weather = dict()

weathers = dict()

def read_race_file(file_path):
    with open(file_path, "r") as file:
        full_data = json.load(file)

    

def main():
    read_race_file("example4.json") 


if __name__ == "__main__":
    main()