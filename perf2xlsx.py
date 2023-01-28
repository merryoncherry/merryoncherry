import argparse
import xlsxwriter

# Read the JSON of each perf report
# Order is determined by first file of occurence for item

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', help="Path to output worksheed")  

args = parser.parse_args()

ofn = args.output
if not ofn:
    ofn = 'xlPerf.xlsx'

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook(ofn)
worksheet = workbook.add_worksheet('Summary')

# Some data we want to write to the worksheet.
expenses = (
    ['Rent', 1000],
    ['Gas',   100],
    ['Food',  300],
    ['Gym',    50],
)

# Start from the first cell. Rows and columns are zero indexed.
row = 0
col = 0

# Iterate over the data and write it out row by row.
for item, cost in (expenses):
    worksheet.write(row, col,     item)
    worksheet.write(row, col + 1, cost)
    row += 1

# Write a total using a formula.
worksheet.write(row, 0, 'Total')
worksheet.write(row, 1, '=SUM(B1:B4)')

workbook.close()
