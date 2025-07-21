"""
import csv

print('Starting Test.py')

total = 0
with open('data.csv', 'r', newline='') as file:
    reader = csv.DictReader(file)
    for row in reader:
        total += int(row['Amount'])

print("Sum of Amount column:", total)
"""

"""
# program to print a variable received from terminal
import sys
if len(sys.argv) > 1:
    print("Received variable:", sys.argv[1])
print("End of Test.py")
"""


          