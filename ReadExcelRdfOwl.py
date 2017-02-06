# coding: utf-8

import openpyxl


def coord(row, col):
    # deprecated workbook.sheet.cell(row,col): use coord : gives 'A1' for (0,0) etc.
    ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    offset = divmod(col,26)
    nameCol=''
    for k in range(0,offset[0]):
        nameCol+='A'
    nameCol+=ascii_uppercase[offset[1]]
    return nameCol+str(row+1)


def getPrefix(wb):
    PREFIX = 'PREFIX'
    # uppercase to avoid pbs
    sheets=[x.upper() for x in wb.get_sheet_names()]
    if PREFIX in sheets :
        sheet = wb.get_sheet_by_name(wb.get_sheet_names()[sheets.index(PREFIX)])
        prefix = []
        for row in range(1, 100):
            p = sheet[coord(row, 0)].value
            if p is not None:
                u = sheet[coord(row, 1)].value
                prefix=prefix+[p, u]
        print prefix



# open excel and get sheets name
excelFileName="D:\python\RDFOWLTests\Ontologie000.xlsx"
wb = openpyxl.load_workbook(excelFileName)
getPrefix(wb)



