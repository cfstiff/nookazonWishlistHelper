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

        strVarName = variantName + ' ' if variantName else ''

        userCheck = input("Found item " + strVarName + productName +
                          ". Is this correct? (Y/N)")
        if userCheck.lower() == 'y':
            validate = True

    mode = input(
        "Please select mode -  1 for Nookazon Catalog, 2 for Nookazon listings, 3 for specific item lookup" + '\n')
    if mode == '1' or mode == '2':
        nookazonID = input(
            "Please enter your Nookazon ID (the number after profile in the URL)" + '\n')
    elif mode == '3':
        items = input(
            "Please enter a comma separated list of items that you would like to search for. Do not include variant - you will set this later" + '\n')
    else:
        return("Invalid mode entered, please restart the program")

    if mode == '1':
        ownedItems = getNookazonCatalogItems(nookazonID)
    elif mode == '2':
        ownedItems = getNookazonListingItems(nookazonID)
    else:
        ownedItems = parseSeparateItems(
            [x.lower().strip() for x in items.split(',')])

    wishlistSellerMap = getWishlistOffers(productID)
    for seller in wishlistSellerMap.keys():
        wishlistItems = getWishlistItems(seller, wishlistSellerMap[seller])
        matches = getMatches(wishlistItems, ownedItems)

        if len(matches) != 0:
            listingURL = getListingLink(seller, productID, variantName)
            print("Listing: " + listingURL)
            print("Matched items: " + str(matches))
    

       


def getProductAndVariantName(searchString):
    productName, productID = getProductName(searchString)
    variantName = getVariantName(productID, productName)

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
        print("No item found for search " + searchTerm)
        newTerm = input("Input new search term: ")
        return getProductName(newTerm)
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


def getVariantName(productID, productName=None):
    payload = {'id': productID, 'variants': ''}
    request = requests.get("https://nookazon.com/api/items", payload)
    json = request.json()

    variants = json['items'][0]['variants']
    diy = json['items'][0]['diy']
    if variants or diy:
        print("Variants and/or DIY Recipe found " +
              ("for item " + productName if productName else " "))
        userIn = input(
            "Press y if you would like to specify a variant or DIY" + '\n')

        if (userIn == 'y' or userIn == 'Y'):
            if diy:
                print("0: DIY Recipe")

            if variants:
                for i in range(len(variants)):
                    print(str(i + 1) + ": " + variants[i]['name'])

            print("Press Q to not specify a variant")
            print(
                "Note - you cannot specify the crafted version of an object at this time")

            variationName = None
            while variationName == None:
                index = input(
                    "Please enter the number of the variant you want" + '\n')
                try:
                    print(index)
                    if index == str(0):
                        variationName = 'diy'
                    elif index == 'Q' or index == 'q':
                        return None
                    else:
                        variationName = variants[int(index) - 1]['name']

                except:
                    print("Invalid entry, please try again")
                    variationName = None

            return variationName.lower()
        else:
            return None
        return variationName.lower()
    return None


def getMatches(wishlistItems, ownedItems):
    matches = []
    for listing in wishlistItems['listings']:
        itemName = listing['name'].lower()
        if itemName in ownedItems.keys() and len(ownedItems[itemName]) != 0:
            if not listing['variant_name'] and listing['diy'] != True:
                matches.append(itemName)
            elif listing['diy'] == True:
                if 'diy' in ownedItems[itemName]:
                    matches.append(itemName + "DIY Recipe")
            else:
                variantName = listing['variant_name'].lower()
                if variantName in ownedItems[itemName]:
                    matches.append((variantName +
                                    " " + itemName))

    return matches


def getNookazonListingItems(sellerID):

    payload = {'auction': False, 'seller': sellerID}
    request = requests.get('https://nookazon.com/api/listings', payload)
    json = request.json()

    ownedItems = defaultdict(list)
    for listing in json['listings']:
        itemName = listing['name'].lower()
        if listing['diy'] == True:
            variantName = 'diy'
        elif listing['variant_name']:
            variantName = listing['variant_name'].lower()
        else:
            variantName = 'None'
        ownedItems[itemName] += [variantName]

    return ownedItems


def getNookazonCatalogItems(sellerID):
    payload = {'user': sellerID}
    request = requests.get('https://nookazon.com/api/catalog', payload)
    json = request.json()

    ownedItems = defaultdict(list)
    for item in json['catalog']:
        variantName = 'None'
        itemName = item['name'].lower()
        if item['diy'] == True:
            variantName = 'diy'
        elif item['variant_id']:
            # Get all variants
            variant_payload = {'id': item['id'], 'variants': ''}
            request = requests.get(
                "https://nookazon.com/api/items", variant_payload)
            json = request.json()
            variants = json['items'][0]['variants']
            for variant in variants:
                if str(variant['id']) == item['variant_id']:
                    variantName = variant['name'].lower()
                    break
        else:
            variantName = 'None'
        ownedItems[itemName] += [variantName]

    return ownedItems


def parseSeparateItems(itemList):
    ownedItems = defaultdict(list)
    for item in itemList:
        productName, variantName, _ = getProductAndVariantName(item)
        ownedItems[productName] += [variantName if variantName else 'None']

    return ownedItems


def getListingLink(sellerID, productID, variantName=None):

    payload = {'seller': sellerID, 'item_id': productID, 'auction': 'false'}
    if variantName:
        if variantName == 'diy':
            payload['diy'] = 'true'
        else:
            payload['variant_name'] = variantName

    request = requests.get('https://nookazon.com/api/listings', payload)
    json = request.json()

    if len(json['listings']) == 0:
        return
    return 'https://nookazon.com/listing/' + json['listings'][0]['id']


if __name__ == "__main__":
    main()
