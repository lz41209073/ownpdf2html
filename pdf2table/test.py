#!/usr/bin/python
# -*- coding: UTF-8 -*-
a = '中文'
print a
a = str(a).decode("string_escape")
print a


t = Table(tables[0],html)
t.set_table_cells(0)
wb = xlwt.Workbook()
sheet = wb.add_sheet('tables',cell_overwrite_ok=True)
for i in [1]:
    for cell in t.cells:
        if cell.covers:
            if len(cell.covers) > 1:
                top_row = cell.covers[0][0]
                bottom_row = cell.covers[-1][0]
                left_column = cell.covers[0][1]
                right_column = cell.covers[-1][1]
                if util.is_number(cell.text):  # if cell.text is number, save in number style
                    content = cell.text.replace(',', '')
                    if content.isdigit():
                        sheet.write_merge(top_row, bottom_row, left_column, right_column, float(content))
                    else:
                        sheet.write_merge(top_row, bottom_row, left_column, right_column, cell.text)
                else:
                    sheet.write_merge(top_row, bottom_row, left_column, right_column, cell.text)
            else:
                if util.is_number(cell.text):
                    content = cell.text.replace(',', '')
                    if content.isdigit():
                        sheet.write(cell.covers[0][0], cell.covers[0][1], float(content))
                    else:
                        sheet.write(cell.covers[0][0], cell.covers[0][1], cell.text)
                else:
                    sheet.write(cell.covers[0][0], cell.covers[0][1], cell.text)
wb.save('11111111.xls')
