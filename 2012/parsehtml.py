#!/usr/bin/env python
# parsehtml.py - Clean up scraped html tables from in.gov.
from bs4 import BeautifulSoup
import csv
import re
import os, os.path

def main():
    """
    Table of contents for the script
    """
    parse_html_files()

# The main program
def parse_html_files():
    folder = os.listdir()
    for file in folder:
        if file.endswith('.html'):
            print("Now working on " + file + ".")
            soup = BeautifulSoup(open(file), "html.parser")
            # Running-mate info is in "i" tags, so toss them.
            for extra in soup.findAll("i"): 
                extra.decompose()
            table = soup.find('table')
            county = file.replace(".html", "").split('_')[2]
            csv_file = file.replace(".html", ".csv")
            with open(csv_file, "w", newline='') as csvfile:
                w = csv.writer(csvfile)
                for row in table.findAll("tr")[1:]:
                    cells = row.findAll("td")
                    # Do different things for rows that have 4, 3, and 2 cells because html rowspan.
                    if len(cells) == 4:
                        office = cells[0].text
                        district = cells[1].text
                        candidate = cells[2]
                        candidate = candidate.text
                        party = cells[2].find('em').text
                        votes = cells[3].text
                        clean_office = clean_text(office)
                        clean_district = clean_text(district)
                        clean_candidate = clean_candidate_text(candidate)
                        clean_party = clean_party_text(party)
                        clean_votes = clean_text(votes)
                        completed_row = [clean_office, clean_district, clean_candidate, clean_party, clean_votes]
                        w.writerow([county, clean_office, clean_district, clean_candidate, clean_party, clean_votes])
                    # Save new row so the next one can compare for missing cells due to rowspan
                        prevline = completed_row

                    elif len(cells) == 3:
                        # This one copies only one cell (office) since it contains district already
                        office = prevline[0]
                        district = cells[0].text
                        candidate = cells[1]
                        # Get rid of running mate in cell
                        candidate = candidate.text
                        party = cells[1].find('em').text
                        votes = cells[2].text
                        clean_office = clean_text(office)
                        clean_district = clean_text(district)
                        clean_candidate = clean_candidate_text(candidate)
                        clean_party = clean_party_text(party)
                        clean_votes = clean_text(votes)
                        completed_row = [clean_office, clean_district, clean_candidate, clean_party, clean_votes]
                        w.writerow([county, clean_office, clean_district, clean_candidate, clean_party, clean_votes])
                        prevline = completed_row


                    elif len(cells) == 2:
                        # Compensate the 2-cell rows who are missing both "office" and "district" cells
                        office = prevline[0]
                        district = prevline[1]
                        candidate = cells[0]
                        # Get rid of running mate in cell
                        candidate = candidate.text
                        party = cells[0].find('em').text
                        votes = cells[1].text
                        clean_office = clean_text(office)
                        clean_district = clean_text(district)
                        clean_candidate = clean_candidate_text(candidate)
                        clean_party = clean_party_text(party)
                        clean_votes = clean_text(votes)
                        completed_row = [clean_office, clean_district, clean_candidate, clean_party, clean_votes]
                        w.writerow([county, clean_office, clean_district, clean_candidate, clean_party, clean_votes])
                        prevline = completed_row

def clean_text(text):
    text = text.strip()
    text = text.replace('  ', ' ')
    return text

def clean_candidate_text(text):
    text = re.sub('[(.)]', '', text)
    text = text.split('  ', 1)[0]
    text = text.split('\n', 1)[0]
    text = ' '.join(reversed(text.split(', ')))
    text = text.replace('  ', ' ')
    if 'JR' in text.upper():
        text = text.upper().replace(' JR','')
        return text + ', Jr.'
    else:
        return text.title()

def clean_party_text(text):
    text = re.sub('[()]', '', text)
    text = re.sub('w/i', '', text.lower())
    return text.title().strip()

if __name__ == "__main__":
    main()
