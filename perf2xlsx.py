import argparse
import json
import xlsxwriter

# Read the JSON of each perf report
# Order is determined by first file of occurence for item

# python perf2xlsx.py -o RenderPerfComp.xlsx M:\xL_Test_2021\2021_Aspirational_Perf_2021_39\perf_report.json  M:\xL_Test_2021\2021_Aspirational_Perf_2022_13\perf_report.json  M:\xL_Test_2021\2021_Aspirational_Perf_2022_26\perf_report.json 
# python perf2xlsx.py -o RenderPerfComp22.xlsx M:\xL_Test_2022\2022_Perf_master\perf_report.json  M:\xL_Test_2022\2022_Perf_branch\perf_report.json 

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', help="Path to output worksheet")  
parser.add_argument('files', nargs='*', help="Input files")

args = parser.parse_args()

ofn = args.output
if not ofn:
    ofn = 'xlPerf.xlsx'

jsons = []
for fn in args.files:
    with open(fn, 'r') as fh:
        jsons.append(json.load(fh))

# Summary
# start_xlights_start
# start_xlights_end
# stop_xlightx_start
# stop_xlights_end

# Per Suite
# switch folder start end

# Per test
# cmp_start, cmp_end
# crc_start, crc_end
# start_batch, end_batch
# start_/end_ open/render/save/close

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook(ofn)

# Add a bold format to use to highlight cells.
bold = workbook.add_format({'bold': True})

# Add a number format for cells with money.
# money = workbook.add_format({'num_format': '$#,###'})

worksheet = workbook.add_worksheet('Summary')
# Header
worksheet.write(0, 0, 'Event', bold)
c = 1
r = {}
nr = 1
for j in jsons:
    worksheet.write(0, c, args.files[c-1], bold)
    for k in j.keys():
        if k.startswith('start_'):
            bk = k[6:]
            ek = 'end_' + bk
            if bk in r:
                row = r[bk]
            else:
                row = nr
                nr = nr + 1
                r[bk] = row
                worksheet.write(row, 0, bk)
            worksheet.write(row, c, j[ek]-j[k])
    c = c + 1

worksheet = workbook.add_worksheet('BatchRender')
worksheet.write(0, 0, 'Suite', bold)
worksheet.write(0, 1, 'Sequence', bold)
c = 0
col = 2
nr = 1
r = {}
for j in jsons:
    c = c + 1
    if 'render_batch' not in j:
        continue
    worksheet.write(0, col, args.files[c-1], bold)

    for o in j['render_batch']:
        suite = o['suite']
        seq = o['seq_name']
        st = o['start_batch']
        et = o['end_batch']
        if (suite, seq) in r:
            row = r[(suite, seq)]
        else:
            row = nr
            nr = nr + 1
            r[(suite, seq)] = row
            worksheet.write(row, 0, suite)
            worksheet.write(row, 1, seq)
        worksheet.write(row, col, et-st)
    col = col + 1


workbook.close()
