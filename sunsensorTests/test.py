import csv

values = [242,242,242,242,242,242,242,242,242,242,242,242,242,242,242,242]

print("What is the name of this document? Make sure to write <name>.csv")
docname = input()

file = open('calibrationData//'+ str(docname), 'w', newline='')
writer = csv.writer(file)

for i in range(3):
    print("When ready to start calibrating, press any button:")
    input1 = input()
    # create the csv writer
    for i in range(10):
        full = [i] + values
        writer.writerow(full)
file.close();