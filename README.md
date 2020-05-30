## Description  
Ever wanted to buy something on Nookazon, only to get overwhelmed trying to look at a bunch of different seller's wishlists? This script allows you to quickly see if you have any items on the wishlist of _any_ seller for a given item. 

Currently supports importing from your Nookazon Catalog, Nookazon Listings, or a list of items.



## Requirements
- Python 3.7
    (it is likely this will also work on any Python > 3, but no guarantees

## Usage
1. `git clone` the repository
2. Install the requirements using `pip3 install -r requirements.txt` or `pip install -r requirements.txt`
3. Run `python3 main.py` in the terminal of your choice
4. Follow the prompts

## Gotchas
- When entering items, make sure to enter the basic version, not a variation (aka, enter `Traditional Tea Set` not `Floral Traditional Tea Set`)
- If no outputs appear, there likely were no matches for your search
- If an item a) has a DIY recipe, and b) has no variations, you cannot search for the DIY on its own. If you search for no variation, you will get listings for both the crafted version and the DIY.
- To get your Nookazon ID, go to your profile on Nookazon. The URL should look something like 
`https://nookazon.com/profile/<number>` - your ID is that number
- This does not search auctions

