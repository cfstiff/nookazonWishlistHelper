from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import re

NOOKAZON_URL = "http://nookazon.com"


def main():
    productID = input(
        "Hello - what item are you looking for? Please use nookazon product ID" + '\n')

    mode = input(
        "Please select mode - 1 for VillagerDB lookup, 2 for Nookazon listings, 3 for specific item lookup" + '\n')
    if mode == '1':
        dbURL = input("Please enter VillagerDB list URL" + '\n')
    elif mode == '2':
        nookazonURL = input("Please enter Nookazon listings URL" + '\n')
    elif mode == '3':
        items = input(
            "Please enter a comma separated list of items that you would like to search for")
    else:
        return("Invalid mode entered, please restart the program")

    driver = webdriver.Firefox()
    if mode == '1':
        OWNED_ITEMS = getVillagerDBOwnedItems(dbURL, driver)
    elif mode == '2':
        OWNED_ITEMS = getNookazonOwnedItems(nookazonURL, driver)
    else:
        OWNED_ITEMS = items
    print("OWNED ITEMS: ")
    print(OWNED_ITEMS)
    wishlists = getWishlistURLs(productID, driver)
    matches = getMatches(wishlists, driver, OWNED_ITEMS)
    print(matches)
    driver.quit()


def getMatches(wishlists, driver, OWNED_ITEMS):
    matches = {}
    for wishlist in wishlists:
        url = NOOKAZON_URL + wishlist
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, features="lxml")

        current_matches = []
        for listing in soup.find_all(class_="listing-name"):
            item = listing.string
            if (item.split()[0].isdigit()):
                item_name = (' ').join(item.split()[2:]).lower()
            else:
                item_name = item.lower()

            if item_name in OWNED_ITEMS:
                current_matches.append(item_name)
                print("MATCHED: " + item_name)
            else:
                print("NOT MATCHED: " + item_name)
        if len(current_matches) != 0:
            matches[wishlist] = current_matches

    return matches


def getWishlistURLs(productID, driver):
    url = "https://nookazon.com/product/" + str(productID)

    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, features="lxml")

    listings = soup.find_all(class_="listing-content")
    wishlistURLs = []
    for listing in listings:

        wishlistURL = listing.find(href=re.compile("wishlist"))
        if wishlistURL:
            wishlistURLs.append(wishlistURL['href'])

    return wishlistURLs


def getVillagerDBOwnedItems(villagerDBUrl, driver):

    driver.get(villagerDBUrl)
    html = driver.page_source
    soup = BeautifulSoup(html, features="lxml")

    items = soup.find_all(class_="list-group-item")
    owned_items = []
    for item in items:
        print(item)
        item_name = item.get('data-name')
        if '(Recipe)' in item_name:
            item_name = ' '.join(item_name.split()[:-1]) + ' diy recipe'
        elif '(' in item_name.split()[-1]:
            modifier = item_name.split()[-1]
            item_name = modifier[1:-1] + ' ' + ' '.join(item_name.split()[:-1])
        owned_items.append(item_name.lower().strip())
    return owned_items


def getNookazonOwnedItems(nookazonURL, driver):

    url = nookazonURL
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, features="lxml")
    items = []
    for listing in soup.find_all(class_="listing-name"):
        item = listing.string
        if (item.split()[0].isdigit()):
            item_name = (' ').join(item.split()[2:]).lower()
        else:
            item_name = item.lower()
        items.append(item_name)

    return items
