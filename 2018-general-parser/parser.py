''' 
Description: Parse out election data from Indiana pdf's
 & Year: Clay 2018, Marshall 2018, Dubois 2018, Shelby 2018
Author: Karen Santamaria   
Date Last Edited: Oct. 28, 2019
'''


import csv
import pdftotext
from table import Table, Row
import re
import os
from os import listdir
from os.path import isfile, join



office_names = [
    "President",
    "U.S. Senate",
    "U.S. House",
    "State Senate",
    "State House",
    "Governor",
    "Attorney General",
    "State Treasurer",
    "Secretary of State"]

def is_int(s):
    '''check if a value is an integer'''
    try: 
        int(s)
        return True
    except ValueError:
        return False

def is_candidate_row(line):
    '''check if line is a candidate row with candidate name and votes'''
    return (len(line) > 5 
            and len(line) < 12 
            and is_int(line[0]) 
            and line[3] != '[Election'
            and line[-1].lower() != 'yes' 
            and line[-1].lower() != 'no')
    
def is_office_name(line):
    '''check if the next line is an office name'''
    return (line[0] == 'VOTE')

def is_precinct_name(line):
    '''check if line contains precinct name'''
    return('Precinct Name:' in ' '.join(line))

def is_county_name(line):
    '''check if line contains county name'''
    return (len(line) == 3 and line[1] == 'County,')

def list_to_string(line):
    '''change list to string'''
    return ' '.join(line)

def create_row(office, district, precinct, county, candidate_line):
    '''create row object'''
    total_vote = candidate_line[3]
    party = get_party(candidate_line)
    candidate = get_candidate(candidate_line)
    row = Row(precinct, office, district, party, candidate, total_vote)
    return row

def get_no_letter(strng):
    return re.sub(r'[^0-9]+', '', strng)
    
def get_district(office_lst):
    '''
    extract district number if present
    VOTES= 452 State Representative District 17 -> 17
    '''
    
    district = ''
    for i in range(1, len(office_lst)-1):
        if('dist' in office_lst[i].lower()):
            if(is_int(get_no_letter(office_lst[i+1]))): 
                # if district number after office name
                district = get_no_letter(office_lst[i+1])
            elif(is_int(get_no_letter(office_lst[i+1]))):
                # if district number before office name
                district = get_no_letter(office_lst[i-1])      
    return district

def get_party(candidate_line):
    '''
    get party from a candidate line
    ['16', '10', '0', '26', '7.22%', '(L)', 'Lucy', 'M', 'Brenton'] -> L
    '''
    party = ''
    if not (candidate_line[5].lower() == 'write-in' 
            or candidate_line[5].lower == 'yes'
            or candidate_line[5].lower == 'no'):
        if(candidate_line[5] == '(R)'):
            party = 'R'
        elif(candidate_line[5] == '(D)'):
            party = 'D'
        elif(candidate_line[5] == "(L)"):
            party = 'L'
    return party
    
    
def get_candidate(candidate_line):
    '''get name from a candidate line
    ['16', '10', '0', '26', '7.22%', '(L)', 'JANE', 'M', 'DOE'] -> Jane M Doe
    '''
    candidate = ''
    if(candidate_line[5].lower() == 'write-in'):
        candidate = 'Write-In'
    else:
        for i in range(6, len(candidate_line)):
            candidate_line[i] = candidate_line[i].capitalize() #JANE DOE -> Jane Doe
        candidate = list_to_string(candidate_line[6:])
    return candidate

def get_precinct(precinct_line):
    '''get precinct name formatted'''
    precinct = precinct_line[2:]
    for i in range(0, len(precinct)):
        precinct[i] = precinct[i].capitalize()  
    
    return list_to_string(precinct)

def import_pdf(filename):
    '''import pdf and get a list that contains all the lines in list format'''
    with open(filename, "rb") as f:
        pdf = pdftotext.PDF(f)
        
    formatted_lines = []
    for page in pdf:
        lines = page.split('\n')
        for i in range(0, len(lines)):
            lines[i] = lines[i].replace('•', '')
            line_lst = ' '.join(lines[i].split()).split(' ')
            formatted_lines.append(line_lst)
    return formatted_lines

def get_office(line):
    '''
    get string line and output office
    VOTES= 371 United States Senator -> U.S. Senate
    US Representative District 2 -> State Representative
    '''

    office = line
    if('=' in office):
        office = office.replace('VOTES', '')
        office = office.replace('=', '')
        office = office.strip()
    if(is_int(office.split(' ')[0])):
        office = list_to_string(office.split(' ')[1:])
    
    if('representative district' in office.lower()):
        office = 'U.S. House'
    elif('state representative district' in office.lower()):
        office = 'State Representative'
    elif('united states Senator' in office.lower() or 'State Senator'.lower() in office.lower()):
        office = 'U.S. Senate'
    elif('secretary of state' in office.lower()):
        office = 'Secretary of State'
    elif('treasurer of state' in office.lower()):
        office = 'State Treasurer'
    return office
    
           
def create_table(formatted_lines):
    '''create table to make csv'''
    table = Table()
    cur_office = ''
    cur_precinct = ''
    cur_county = ''
    cur_district = ''
    for i in range(0, len(formatted_lines)): 
        cur_line = formatted_lines[i]
        if(is_candidate_row(cur_line) and cur_office in office_names):
            row = create_row(cur_office, cur_district, cur_precinct, cur_county, cur_line)
            
            table.add_to_table(row)
        elif(is_office_name(cur_line)):
            cur_district = get_district(formatted_lines[i+1])
            cur_office = get_office(list_to_string(formatted_lines[i+1]).strip())
        elif(is_precinct_name(cur_line)):
            cur_precinct = get_precinct(cur_line)
        elif(is_county_name(cur_line)):
            cur_county = cur_line[0]
    
    return table

def get_out_filename(formatted_lines):
    '''get filename for csv output'''
    filename = '__in__general__' +  get_county_name(formatted_lines) +' county.csv'
    
    if(len(formatted_lines) > 1 and 
       len(formatted_lines[-2]) > 5 and 
       len(formatted_lines[-2][5])> 0):
        date_lst = formatted_lines[-2][5][:-1].split('/')
        
        if (len(date_lst) == 3):
            
            year = date_lst[2]
            month = date_lst[0]
            day = date_lst[1]
            
            if (len(month) == 1):
                month = '0' + month
            if (len(day) == 1):
                day = '0' + day
        
            filename = year + month + day + filename
    
    return filename

def get_county_name(formatted_lines):
    '''get county name for filename'''
    county = ''
    for cur_line in formatted_lines:
        if (is_county_name(cur_line)):
            return cur_line[0].lower()
    return county

def main():
    in_filepath = input('Enter file to parse: ')
    imported_pdf = import_pdf(in_filepath)
    table = create_table(imported_pdf)
    filename = get_out_filename(imported_pdf)
    
    out_filepath = input('Enter disired output folder: ')
    
    table.convert_to_csv(out_filepath + filename)
        

if __name__ == "__main__":
    main()

