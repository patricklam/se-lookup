#!/usr/bin/python3

import csv
import os
import re
import readline
from pathlib import Path
from operator import attrgetter

DATADIR=Path(os.path.dirname(os.path.realpath(__file__))) / "data"

class Term:
  def __init__(self, level, term_name):
    self.level = level
    self.term_name = term_name

  def __str__(self):
    return '[{}: {}]'.format(self.level, self.term_name)

  def __gt__(self, other):
    return self.level > other.level
    
class Student:
  def __init__(self, id, first_name, preferred_name, last_name, watid, email, terms):
    self.id = id
    self.first_name = first_name
    self.preferred_name = preferred_name
    self.last_name = last_name
    self.watid = watid
    self.email = email
    self.terms = terms

    self.update_names_for_search()

  def update_names_for_search(self):
    self.first_names_for_search = [str.lower(self.first_name)]
    if self.preferred_name:
      self.first_names_for_search.append(str.lower(self.preferred_name))
    if ' ' in self.first_name:
      self.first_names_for_search.extend(str.lower(self.first_name).split(' '))
    self.last_name_for_search = str.lower(self.last_name)
    
  def class_of(self):
    level_dict = { "1A": 5, "1B": 4, "2A": 4, "2B": 3, "3A": 3, "3B": 2, "4A": 1, "4B": 0 }
    latest = 0
    for term in self.terms:
      year = int(term.term_name[1:3])
      this_students_year = year + level_dict[term.level]
      if this_students_year > latest:
        latest = this_students_year
    return latest
    
  def __str__(self):
    fname = ('{} [{}]'.format(self.preferred_name, self.first_name)) if self.preferred_name else self.first_name
    terms = ' '.join(map(str, sorted(self.terms)))
    return '{} {} <{}>\n SE class of 20{}.\n OAT link: {}\n {} {} ({})\n Registered: {}\n'.format(fname,
                    self.last_name, self.email,
                    self.class_of(),
                    'https://oat.uwaterloo.ca/asis/{}'.format(self.id),
                    fname, self.last_name, self.id,
                    terms)

  def is_strong_match(self, query):
    if (self.id == query):
      return True
    if (self.watid == query):
      return True
    if (self.last_name_for_search == query):
      return True
    for fn in self.first_names_for_search:
      if (fn + ' ' + self.last_name_for_search == query):
        return True
    if ',' in query:
      parts = list(map(str.strip, query.split(',')))
      for fn in self.first_names_for_search:
        if (parts[0] == self.last_name_for_search and parts[1] == fn):
          return True
    return False

      # f[irstname] lastname
  def is_weak_match(self, query):
    if ' ' in query:
      for fn in self.first_names_for_search:
        parts = list(map(str.strip, query.split(' ')))
        if (parts[1] == self.last_name_for_search and fn.startswith(parts[0])):
          return True
    else:
      for fn in self.first_names_for_search:
        if (fn.startswith(query)):
          return True
    if ',' in query:
      parts = list(map(str.strip, query.split(',')))
      for fn in self.first_names_for_search:
        if (parts[0] == self.last_name_for_search and fn.startswith(parts[1])):
          return True
    return False

def convert_to_term(number):
  yr = number[0]
  term = 'A' if number[2] == '1' else 'B'
  return yr + term

def read_students():
  student_dict = {}
  for fname in DATADIR.glob('se-*.csv'):
    term_info = re.match(r"se-(\d0\d)-(\w\d\d).csv", fname.name)
    level = convert_to_term(term_info.group(1))
    term_name = str.upper(term_info.group(2))
    term = Term(level, term_name)
    # print ('Reading term info for ' + level + '/' + term)
    
    with open(fname, 'r', newline='') as input_csv:
      reader = csv.reader(input_csv)
      for row in reader:
        id = row[0]
        if id in student_dict:
          student = student_dict[id]
          # XXX todo ensure other parts of Student class match
          student.terms.append(term)
        else:
          student = Student(id, row[7], '', row[6], str.lower(row[9]), row[10], [term])
          student_dict[id] = student

  try:
    with open(DATADIR / 'additional-data.csv', 'r', newline='') as additional_csv:
      reader = csv.reader(additional_csv, skipinitialspace=True)
      for row in reader:
        if not row:
          continue
        id = row[0]
        if id in student_dict:
          student = student_dict[id]
          student.watid = row[1]
          student.preferred_name = row[2]
          student.last_name = row[3]
          student.update_names_for_search()
        else:
          student = Student(id, row[2], '', row[3], row[1], row[1] + "@edu.uwaterloo.ca", [])
  except FileNotFoundError:
    # not a big deal to have no additional data
    pass
          
  return student_dict.values()

def find_student(q, students):
  query = str.lower(q)
  for student in students:
    if (student.is_strong_match(query)):
      yield student

def find_student_weak(q, students):
  query = str.lower(q)
  for student in students:
    if (student.is_weak_match(query)):
      yield student
      
students = read_students()
try:
  while True:
    query = input('Query: ')
    if not query:
      break

    results = list(find_student(query, students))
    if len(results) > 30:
      print ("Too many matches ({})!".format(len(results)))
      continue

    if not results:
      results = find_student_weak(query, students)
      if results:
        results = list(results)
      else:
        results = []
    if len(results) > 30:
      print ("no strong matches, too many weak matches!")
      continue

    if not results:
      print ("no matches")
    results.sort(key=attrgetter('last_name', 'first_name'))
    for result in results:
      print (result)  
except EOFError:
  pass
