#!/usr/bin/python
# -*- coding: UTF-8 -*-
import numpy as np
from bs4 import BeautifulSoup
import io
import xlwt
excel_forbidden_sign = ['+','-']
import util
#class for cell
class Cell():
  def __init__(self, type, left, right, up, down, text):
    self.type = type
    self.left = left
    self.right = right
    self.up = up
    self.down = down
    self.text = text
    self.row = 1
    self.column = 1
    self.covers = []
    self.next = None
    self.pre = None

  def set_pre_cell(self,cell):
    self.pre = cell

  def set_next_cell(self,cell):
    self.next = cell

#class for row

class Row(object):
  """docstring for Row"""
  def __init__(self,cell_list):
    self.cells = cell_list
    #self.subrow_cells = self.set_subrow_cells()
    self.x_sequence = self.get_x_sequence()
    self.y_sequence = self.get_y_sequence()
    self.set_cell_link()
    self.matrix = None

  def set_cell_link(self):
    for i in range(len(self.cells) - 1):
        cell = self.cells[i]
        cell.next = self.cells[i + 1]

  # get start and end points of cells in one row
  def get_x_sequence(self):
      x_list = set()
      for cell in self.cells:
          x_list.add(cell.left)
      x_list = sorted(list(x_list))
      return x_list

  # get start and end points of cells in one row
  def get_y_sequence(self):
      y_list = set()
      for cell in self.cells:
          y_list.add(cell.down)
      y_list = sorted(list(y_list),reverse=True)
      return y_list

  def set_matrix(self, subrow_num, subcol_num, offset):
      num = subrow_num * subcol_num
      matrix = np.array([''] * num, dtype=object).reshape(subrow_num, subcol_num)
      for cell in self.cells:
          cur_x = self.x_sequence.index(cell.left)
          next_x = len(self.x_sequence)
          if cell.next:
              if cell.next.left not in self.x_sequence: break
              next_x = self.x_sequence.index(cell.next.left)
              if next_x <= cur_x: next_x = len(self.x_sequence)
          cur_y = self.y_sequence.index(cell.down)
          for i in range(cur_y + 1):  # row
              for j in range(cur_x, next_x):  # column
                  if matrix[offset + i][j] == '':
                      if cur_y == i and cur_x == next_x - 1:
                          if cell.text[0] in excel_forbidden_sign:  # filter for excel forbidden string
                              matrix[offset + i][j] = ' ' + cell.text
                          else:
                              matrix[offset + i][j] = cell.text
                      else:
                          if cell.text[0] in excel_forbidden_sign:  # filter for excel forbidden string
                              matrix[offset + i][j] = ' ' + cell.text + "#merge#"
                          else:
                              matrix[offset + i][j] = cell.text + "#merge#"
      self.matrix = matrix  # if cell is not in sequence, return the matrix with ''
      return matrix

  # for merging cells
  def set_cell_covers(self, offset):
      position_set = set()
      for cell in self.cells:
          cur_x = self.x_sequence.index(cell.left)
          next_x = len(self.x_sequence)
          if cell.next:
              next_x = self.x_sequence.index(cell.next.left)
              if next_x <= cur_x: next_x = len(self.x_sequence)
          cur_y = self.y_sequence.index(cell.down)
          cell.row = cur_y + 1
          cell.column = next_x - cur_x
          for i in range(cur_y+1):  # row
              for j in range(cur_x, next_x):  # column
                  position = (offset + i, j)
                  if position not in position_set:
                      cell.covers.append(position)
                      position_set.add(position)

class Table(object):
  """docstring for Table"""
  def __init__(self, divs, html):
      self.divs = divs
      self.html = html
      self.cells = self.__get_cell_info()
      self.rows = self.__get_rows()
      self.size = self.__get_table_size() # tuple (row,column)

      self.info = None

  def __get_cell_info(self):
      cells = []
      for div in self.divs:
          div_class = div['class'] # list type
          for cls in div_class:
              if cls.startswith('x'):
                  query = '.' + cls + '{left:'
                  left = self.get_div_info(query, ';}')
              elif cls.startswith('y'):
                  query = '.' + cls + '{bottom:'
                  down = self.get_div_info(query, ';}')
              elif cls.startswith('w'):
                  query = '.' + cls + '{width:'
                  width = self.get_div_info(query, ';}')
              elif cls.startswith('h'):
                  query = '.' + cls + '{height:'
                  height = self.get_div_info(query, ';}')

          cell = Cell(div_class[0],left,left+width,down+height, down,div.get_text())
          cells.append(cell)
      return cells

  def __get_rows(self):
      lowdown = self.cells[0].down
      rows = []
      start = 0
      for i in range(len(self.cells)):
          cell = self.cells[i]
          if cell.up <= lowdown:
              row = Row(self.cells[start:i])
              rows.append(row)
              start = i
          if cell.down < lowdown:
              lowdown = cell.down
          if i == len(self.cells)-1:
             row = Row(self.cells[start:i+1])
             rows.append(row)
      return rows
    #
    # # detect wheather row of y_sequence is right
    # # find the convex cells of row
    # convex_cells = {}
    # print rows[0].y_sequence
    # print rows[0].x_sequence
    # for i in range(len(rows)):
    #   row = rows[i]
    #   for cell in row.cells:
    #     if cell.y not in row.y_sequence:
    #       convex_cells[cell] = [i]
    #     else:
    #       cur_index = row.y_sequence.index(cell.y)
    #       if cur_index>len(row.y_sequence)-1: # this row is not a rectangle
    #         convex_cells[cell] = [i]
    #
    # if convex_cells: # convex_cells exist
    #   # add row index for convex cells
    #   for cell,row_indexs in convex_cells.items():
    #     init_row = row_indexs[0]
    #     for j in range(init_row+1,len(rows)):
    #       row = rows[j]
    #       convex_cells[cell].append(j)
    #       if row.cells[0].y == cell.y: # first cell of row(for now maybe need changing)
    #         break
    #   # row merge range
    #   min_r = len(rows); max_r = 0
    #   for cell,ranges in convex_cells.items():
    #     if ranges[0]<min_r: min_r = ranges[0]
    #     if ranges[-1]>max_r: max_r = ranges[-1]
    #   # rebuild row
    #   merge_cells = []
    #   for i in range(min_r,max_r+1):
    #     r = rows[i]
    #     merge_cells += r.cells
    #   new_big_row = Row(merge_cells)
    #   if max_r<len(rows)-1:
    #     rows = rows[:min_r]+[new_big_row]+rows[max_r+1:]
    #   else:
    #     rows = rows[:min_r]+[new_big_row]
    # return rows


  def __get_table_size(self):
      max_x_sequence = self.rows[0].x_sequence # init with the first row
      for row in self.rows:
          for i in range(1,len(row.x_sequence)):
              cur_x = row.x_sequence[i]
              pre_x = row.x_sequence[i-1]
              if cur_x not in max_x_sequence and pre_x in max_x_sequence:
                  pre_index = max_x_sequence.index(pre_x)
                  if pre_index == len(max_x_sequence)-1: max_x_sequence.append(cur_x)
                  else:
                      max_x_sequence = max_x_sequence[:pre_index+1]+[cur_x]+max_x_sequence[pre_index+1:]
      matrix_row_num = 0
      for row in self.rows:
          matrix_row_num += len(row.y_sequence)
          row.x_sequence = max_x_sequence
      r = matrix_row_num; c = len(max_x_sequence)
      return (r,c)

  def table2matrix(self):
      r = self.size[0]; c = self.size[1]
      t_matrix = np.array(['']*(r*c),dtype=object).reshape(r,c)
      i = 0
      for row in self.rows:
          row.set_matrix(r,c,i)
          t_matrix += row.matrix
          i += len(row.y_sequence)
      return t_matrix

  # for merging cells
  def set_table_cells(self,offset):
      i = 0
      for row in self.rows:
          row.set_cell_covers(offset+i)
          i += len(row.y_sequence)

  def get_div_info(self, query, endstr):
      bottom = None
      if query:
          start = self.html.find(query)
      if start != -1:
          start += len(query)
          end = self.html.find(endstr,start)
          bottom = self.html[start:end]
          bottom = bottom[:len(bottom)-2]
      return float(bottom)



import io
import os

def load_html(filename):
    lines = []
    with io.open(filename, 'r', errors='ignore') as f:
        for line in f:
            lines.append(line.strip())
    html = ''.join(lines)
    soup = BeautifulSoup(html, 'html.parser')
    pages = soup.select("#page-container > div")
    return html, pages

def extract_table_divs(page):
    content_divs = page.select(".pc > div")
    if not content_divs: return
    div_type_list = []
    for div in content_divs:
        div_class = div['class'] # list type
        div_type = div_class[0]
        div_type_list.append(div_type)
    table_ranges = find_continue_list(div_type_list)
    if not table_ranges: return
    tables = []; description = ''
    for r in table_ranges:
        tables.append(content_divs[r[0]:r[1]])
    return tables

def find_continue_list(type_list):
    table_range_list = []
    if not type_list: return
    start = 0
    while start<len(type_list)-1:
      # pdb.set_trace()
      if type_list[start] == "c":
          end = start+1
          for j in range(start+1,len(type_list)):
              if type_list[j] == "t":
                  end = j
                  if end - start > 1: table_range_list.append([start,end])
                  break
          if j == len(type_list)-1:
              if type_list[j] == "c": table_range_list.append([start,j+1])
              break
          start = end
      start += 1
    return table_range_list









