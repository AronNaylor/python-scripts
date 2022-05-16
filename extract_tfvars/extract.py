import re

pattern = re.compile('(?<=variable\s").*(?="\s{)')
input_file = input("Input file: ")

tfvars = open(input_file, "r")

result = re.findall(pattern, tfvars.read())

f = open("output.txt", "a")

for var in result:
    f.write(f"var.{var}\n")

f.close()

# TODO: Add unit tests