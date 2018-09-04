# SE Name Lookup Tool

## Input: 

lastname
f[irstname] lastname
lastname, firstname
student id
watiam

plus files:
data/se-[1234]0[12]-[fws][year].csv class rosters downloaded from quest
data/additional-data.csv (in format id#, watiam, fname, lname)

## Tools: 

### sanitize.py

Removes marks from se-101-*.csv.

### lookup.py

Performs the lookup. 

Sample input/output:

> p23lam

Patrick Lam (96123456)
SE class of 1999.
Registered as follows: 
[2A: F96] [2B: W97] [3A: F97] [3B: W98] [4A: F98] [4B: F99]

