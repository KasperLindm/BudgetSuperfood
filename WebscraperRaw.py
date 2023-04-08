import requests
from bs4 import BeautifulSoup
import re
import pygsheets
import pandas as pd

keypath = 'C:\\Users\Kaspe\Documents\AuthKeys\superfoods-383120-9880791a7067.json'
gc = pygsheets.authorize(service_file=keypath)
sh = gc.open("Superfoods")

def CleanNumber(numElement):
    numElement = numElement.get_text().strip().replace(u'\xa0', u' ')
    numElement = numElement.replace(u',', u'.')
    numElement = re.findall("\d+\.\d+", numElement)[0]
    return numElement

def CleanFloat(floatElement):
    floatElement = re.findall("\d+\.\d+", floatElement)[0]
    return floatElement


def InsertIcaProduct(df, url):
    response = requests.get(url)
    soup_data = BeautifulSoup(response.text, 'html.parser')
   
    title  = soup_data.findAll('h1', {"class": "heading__Base-sc-1vuwqc7-0-h1 sc-ehCIER ZBWKl rZSBo"})
   
    contents = soup_data.findAll('div', {"class": "static-content-wrapper__StaticContentWrapper-sc-3z5iao-0 fdAbME"})
    contents.reverse()
    
    kg_price = soup_data.findAll('span', {"class": "text__Text-sc-6l1yjp-0 bhymDA"})
    kg_price = CleanNumber(kg_price[1])
    
    price = soup_data.findAll('div', {"class" : "spacing__Spacing-sc-ngu0v9-0 lbarHM"})
    price = CleanNumber(price[0])

    df.loc[len(df)+1] = [title[0].text.strip(), contents[0].text.strip(), kg_price, price, url]
    return [df]

df = pd.DataFrame(columns=['product','nutrients', 'kg_price', 'price','link'])

for value in sh[1].get_all_values():
    InsertIcaProduct(df, value[0])

df[['kcal', 'kj', 'fat','sat_fat', 'carb', 'sugar', 'fiber','protein','salt']] = df['nutrients'].str.split(",", expand=True)
df = df.drop(['nutrients'], axis=1)

df.kcal = df.kcal.str.extract("(\d+)")
df.kj = df.kj.str.extract("(\d+)")
df.fat = df.fat.str.extract("(\d+)")
df.sat_fat = df.sat_fat.str.extract("(\d+)")
df.carb = df.carb.str.extract("(\d+)")
df.sugar = df.sugar.str.extract("(\d+)")
df.fiber = df.fiber.str.extract("(\d+)")
df.protein = df.protein.str.extract("(\d+)")
df.salt = df.salt.str.extract("(\d+)")

df['url'] = df.link
df = df.drop(['link'], axis=1)

# Export to sheets and local csv file
df.to_csv('scraped_foods.csv')
wks = sh[0]
wks.set_dataframe(df,(1,1))