#!/usr/bin/env python
# scraper.py - Opens a browser scrapes for IN county-level election results

from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from bs4 import BeautifulSoup
import time

base_url = "http://www.in.gov/apps/sos/election/general/general2014"
# Or for 2014 primary: http://www.in.gov/apps/sos/primary/sos_primary14 
county_list = ["Adams","Allen","Bartholomew","Benton","Blackford","Boone","Brown","Carroll","Cass","Clar","Clay","Clinton","Crawford","Daviess","Dearborn","Decatur","DeKalb","Delaware","Dubois","Elkhart","Fayette","Floyd","Fountain","Franklin","Fulton","Gibson","Grant","Greene","Hamilton","Hancock","Harrison","Hendricks","Henry","Howard","Huntington","Jackson","Jasper","Jay","Jefferson","Jennings","Johnson","Knox","Kosciusko","LaGrange","Lake","LaPort","Lawrence","Madison","Marion","Marshall","Martin","Miami","Monroe","Montgomery","Morgan","Newton","Noble","Ohio","Orange","Owen","Parke","Perry","Pike","Porter","Posey","Pulaski","Putnam","Randolph","Ripley","Rush","Saint Joseph","Scott","Shelby","Spencer","Starke","Steuben","Sullivan","Switzerland","Tippecanoe","Tipton","Union","Vanderburgh","Vermillion","Vigo","Wabash","Warren","Warrick","Washington","Wayne","Wells","White","Whitley"]
browser = webdriver.Firefox()

def main():
    """
    Table of contents for the script
    """
    scrape_site()

def scrape_site():
    browser.get(base_url)
    time.sleep(5)
    # Find the dropdown menu and submit button to loop through each county option
    dropdown = browser.find_element_by_name("countyID")  # Get the select element
    options = dropdown.find_elements_by_tag_name("option") # Get all the options

    optionsList = []
    for option in options: #iterate over the options and put them into optionsList
        optionsList.append(option.get_attribute('value'))

    # Loop through county values starting with the second option value since first is main page
    for optionValue in optionsList[1:]:
        # print(optionValue)
        print("Getting info for " + county_list[int(optionValue) - 1] + " County.")
        select = Select(browser.find_element_by_name("countyID"))
        select.select_by_value(optionValue)
        submit_btn = browser.find_element_by_name("trCounty")
        submit_btn.click()
        html = browser.page_source
        soup = BeautifulSoup(html, "html.parser")   
        table = soup.find('table', attrs={'border': '1'})
        # Use the option values as county_list index and subtract 1 to make up for skipped first page
        with open("2014_General_" + county_list[int(optionValue) - 1] + ".html", "w") as outfile:
            outfile.write(str(table))
        browser.get(base_url)

if __name__ == "__main__":
    main()
