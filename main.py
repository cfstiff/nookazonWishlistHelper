from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import re
from collections import defaultdict

NOOKAZON_URL = "http://nookazon.com"


def main():
    validate = False
    while validate == False:
        userProductNameInput = input(
            "Hello - what item are you looking for?" + '\n')

        productName, variantName, productID = getProductAndVariantName(
            userProductNameInput)

        userCheck = input("Found item " + productName +
                          ". Is this correct? (Y/N)")
        if userCheck.lower() == 'y':
            validate = True

    mode = input(
        "Please select mode - 1 for VillagerDB lookup, 2 for Nookazon listings, 3 for specific item lookup" + '\n')
    if mode == '1':
        dbURL = input("Please enter VillagerDB list URL" + '\n')
    elif mode == '2':
        nookazonID = input(
            "Please enter your Nookzon ID (the number after profile in the URL)" + '\n')
    elif mode == '3':
        items = input(
            "Please enter a comma separated list of items that you would like to search for" + '\n')
    else:
        return("Invalid mode entered, please restart the program")

    if mode == '1':
        return
        # OWNED_ITEMS = getVillagerDBOwnedItems(dbURL, driver)
    elif mode == '2':
        ownedItems = getNookazonOwnedItems(nookazonID)
    else:
        return
        # OWNED_ITEMS = [x.lower().strip() for x in items.split(',')]

    wishlistSellerMap = getWishlistOffers(productID)
    for seller in wishlistSellerMap.keys():
        wishlistItems = getWishlistItems(seller, wishlistSellerMap[seller])
        matches = getMatches(wishlistItems, ownedItems)

        print("Seller ID:" + seller)
        if len(matches) != 0:
            print("Matches for seller " + seller + ":")
            print(matches)


def getProductAndVariantName(searchString):
    productName, productID = getProductName(searchString)
    variantName = getVariantName(productID)

    return [productName, variantName, productID]


def getWishlistItems(sellerID, wishlistID=None):
    payload = {'auction': 'false', 'seller': sellerID,
               'buying': ' ', 'wishlistID': wishlistID}
    request = requests.get(
        "https://nookazon.com/api/listings", payload)

    return request.json()


def getWishlistOffers(itemID):
    payload = {'auction': 'false', 'item': itemID}
    request = requests.get("https://nookazon.com/api/listings", payload)
    jsonObj = request.json()

    listings = jsonObj['listings']

    sellerMap = {}

    for listing in listings:
        if listing['offer_wishlist'] == True:
            sellerMap[listing['seller_id']] = listing['offer_wishlist_id']

    return sellerMap


def getProductName(searchTerm):
    payload = {'search': searchTerm}
    request = requests.get("https://nookazon.com/api/items", payload)
    json = request.json()

    if len(json['items']) == 0:
        print("No item found - please search again")
        return
    elif len(json['items']) == 1:
        itemName = json['items'][0]['name']
        itemID = json['items'][0]['id']
    else:
        print("Multiple items found: ")
        for i in range(len(json['items'])):
            print(str(i) + ": " + json['items'][i]['name'])
        itemName = None
        while itemName == None:
            index = input(
                "Please enter the number of the item you want" + '\n')
            try:
                itemName = json['items'][int(index)]['name']
                itemID = json['items'][int(index)]['id']
            except:
                print("Invalid entry, please try again")
                itemName = None

    return [itemName.lower(), itemID]


def getVariantName(productID):
    payload = {'id': productID, 'variants': ''}
    request = requests.get("https://nookazon.com/api/items", payload)
    json = request.json()

    variants = json['items'][0]['variants']
    if variants:
        print("Variants found - would you like to specify one?")
        userIn = input("Press y if you would like to specify a variant" + '\n')
        if (userIn == 'y' or userIn == 'Y'):
            for i in range(len(variants)):
                print(str(i) + ": " + variants[i]['name'])
            variationName = None
            while variationName == None:
                index = input(
                    "Please enter the number of the variant you want" + '\n')
                try:
                    variationName = variants[int(index)]['name']
                except:
                    print("Invalid entry, please try again")
                    variationName = None
        else:
            return None

        return variationName.lower()
    return None


def getMatches(wishlistItems, ownedItems):
    matches = []
    for listing in wishlistItems['listings']:
        itemName = listing['name'].lower()
        if itemName in ownedItems.keys() and len(ownedItems[itemName]) != 0:
            if not listing['variant_name']:
                matches.append(itemName)
            else:
                variantName = listing['variant_name'].lower()
                if variantName in ownedItems[itemName]:
                    matches.append((variantName +
                                    " " + itemName))

    return matches


def getNookazonOwnedItems(sellerID):

    payload = {'auction': False, 'seller': sellerID}
    request = requests.get('https://nookazon.com/api/listings', payload)
    json = request.json()

    ownedItems = defaultdict(list)
    for listing in json['listings']:
        itemName = listing['name'].lower()
        if listing['variant_name']:
            variantName = listing['variant_name'].lower()
        else:
            variantName = ['None']
        ownedItems[itemName] += [variantName]

    return ownedItems


# OLD CODE BEYOND HERE
def getVillagerDBOwnedItems(villagerDBUrl, driver):

    driver.get(villagerDBUrl)
    html = driver.page_source
    soup = BeautifulSoup(html, features="lxml")

    items = soup.find_all(class_="list-group-item")
    owned_items = []
    for item in items:
        item_name = item.get('data-name')
        if '(Recipe)' in item_name:
            item_name = ' '.join(item_name.split()[:-1]) + ' diy recipe'
        elif '(' in item_name.split()[-1]:
            modifier = item_name.split()[-1]
            item_name = modifier[1:-1] + ' ' + ' '.join(item_name.split()[:-1])
        owned_items.append(item_name.lower().strip())
    return owned_items


if __name__ == "__main__":
    main()
