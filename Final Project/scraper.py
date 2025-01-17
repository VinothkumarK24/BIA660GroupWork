"""
Scrape Data from Scryfall, store it in csv
"""

import csv
import os.path
import re
import requests
import time

from bs4 import BeautifulSoup
from selenium import webdriver

#check if data exists
def checkDataParsed(filename):
    if os.path.exists(filename):
        return True
    else:
        return False

#scrape data (10 000 random sources)
def driverBuilder(url):
    driver = webdriver.Chrome('./chromedriver')
    driver.get(url)
    time.sleep(2)

    return driver


def randomLinkGenerator():
    driver = driverBuilder('http://www.scryfall.com')
    randomCardLink = driver.find_element_by_link_text('Random Card')
    url = randomCardLink.get_attribute('href')
    driver.quit()
    return url

#try and build url request
def requestBuilder(url):
    for i in range(5):
        response=requests.get(url,headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36', })
        if response:
            break
        else:
            time.sleep(2)

    if not response: 
        return None
    else:
        return response

 
#scrape data individual data
def myStrip(scrapedData):
    cleanText = scrapedData.text.strip()

    return cleanText 

def scrapeCard(cardPageText):
    cardData = {'cardName': None,
                'cardCost': None,
                'cardType': None,
                'cardText': None}

    cardSoup = BeautifulSoup(cardPageText, 'lxml') 
    cardName = cardSoup.find('h1', {'class': 'card-text-title'})
    cardCost = cardSoup.find('span', {'class': 'card-text-mana-cost'})
    cardType = cardSoup.find('p', {'class':'card-text-type-line'})
    #TODO: Split out Subtypes   
    cardText = cardSoup.find('div', {'class':'card-text-oracle'})
    
    if cardName and cardCost:
        cardName = myStrip(cardName)
        cardCost = myStrip(cardCost)
        try:
            cardName = cardName.replace(cardCost,'')
        except:
            print('Failed on ' + cardName)
        cardData['cardName'] = cardName.strip()
        cardData['cardCost'] = cardCost
    else:
        if cardName:
            cardData['cardName'] = myStrip(cardName).strip()
        if cardCost:
            cardData['cardCost'] = myStrip(cardCost)
    if cardType:
        cardData['cardType'] = myStrip(cardType)
    if cardText:
        cardData['cardText'] = myStrip(cardText)
    
    return cardData

def csvWriter(cardData, dataFilename):
    if not checkDataParsed(dataFilename):
        with open(dataFilename, 'w', encoding='utf8') as outfile:
            writer = csv.writer(outfile, lineterminator='\n')
            writer.writerow([cardData])
    else:
        with open(dataFilename, 'a', encoding='utf8') as outfile:
            writer = csv.writer(outfile, lineterminator='\n')
            writer.writerow([cardData])

    return

#possible json helper function


def run(dataFilename='trainingCards.txt', rebuildTraining=True, setSize=10000):
    if checkDataParsed(dataFilename) and rebuildTraining==False:
        return
    else:
        #TODO: if rebuild is true delete and restart file
        for i in range(setSize):
            #TODO: Set up an already seen
            url = randomLinkGenerator()
            response = requestBuilder(url)
            cardData = scrapeCard(response.text)
            csvWriter(cardData, dataFilename)
        print('Done')

#run(setSize=1, rebuildTraining=False, dataFilename='authors.txt')
#run(setSize=1, rebuildTraining=False)
#run(setSize=1)
run(setSize=5)