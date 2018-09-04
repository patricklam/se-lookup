#!/usr/bin/python3

import csv
import os
import tempfile
from pathlib import Path

DATADIR=Path(os.path.dirname(os.path.realpath(__file__))) / "data"

for fname in DATADIR.glob('se-101-*.csv'):
  ofname = fname.with_suffix('.tmp')
  output_csv = open(ofname, 'w')
  with open(fname, 'r', newline='') as input_csv:
    writer = csv.writer(output_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    reader = csv.reader(input_csv)
    for row in reader:
      row[5] = ''
      writer.writerow(row)
  os.unlink(fname)
  os.link(ofname, fname)
  os.unlink(ofname)
