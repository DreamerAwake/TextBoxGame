import csv

if __name__ == "__main__":
    with open("items.csv", newline='', encoding='UTF-8') as stylefile:
        style_csv_reader = csv.reader(stylefile)

        style_csv_reader.pop(0)