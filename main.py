#!/usr/bin/python3

from click import command, option
import numpy as np
import pandas as pd
import re
from requests import get
from time import sleep


NEW_PRICE_PATTERN = r"([0-9]+.[0-9]+) \+ shipping"
# NEXT_PAGE_PATTERN = r"(\?page=[0-9]+)\">[0-9]+</a><\/li><li class=\"next_page\">"
NEXT_PAGE_PATTERN = r"next_page\".+\?page=([0-9]+)\">Next"

def find_price(str):
    matchObj = re.search(NEW_PRICE_PATTERN, str)
    if matchObj:
        return float(matchObj.group(1))
    else:
        return np.nan


def create_dataframe_from_url(url):
    data = pd.read_html(url)
    df = data[0]
    return df


def process_dataframe(df):
    df["Price"] = df['Event'].apply(lambda x: find_price(x))
    df.dropna().head()
    df['Date'] = pd.to_datetime(df['Date'])
    return df


def print_lowest_game_price(game,df):
    print("The lowest price for {} was £{} on {} at {}".format(game,df['Price'].min(),df[df['Price']==df['Price'].min()]['Date'].to_string(index=False),df[df['Price']==df['Price'].min()]['Store'].to_string(index=False)))

def print_lowest_price(df):
    print("The lowest price for {} was £{} on {} at {}".format(game,df['Price'].min(),df[df['Price']==df['Price'].min()]['Date'].to_string(index=False),df[df['Price']==df['Price'].min()]['Store'].to_string(index=False)))


def get_dataframes_by_url(url):
    num_pages = 1
    # get first page
    df = create_dataframe_from_url(url)

    sleep(0.5)
    # try to get next page(s)
    response = get(url)
    matchObj = re.search(NEXT_PAGE_PATTERN,response.text)
    while matchObj:
        next_url = url+"?page={}".format(matchObj.group(1))
        print(next_url)
        df_next = create_dataframe_from_url(next_url)
        df = df.append(df_next)
        response = get(next_url)
        matchObj = re.search(NEXT_PAGE_PATTERN,response.text)
        num_pages += 1

    print("{} history pages found.".format(num_pages))
    return df


def generate_pattern(game):
    return r"<a href=\"/item/show/([0-9]+)/(.*)\">"+game+"</a>"


def find_history_url(game):
    PATTERN = generate_pattern(game)
    url = "https://boardgameprices.co.uk/item/search?search="+game
    response = get(url)
    matchObj = re.search(PATTERN,response.text)
    if matchObj:
        hist_url = "https://boardgameprices.co.uk/item/history/{}/{}".format(matchObj.group(1),matchObj.group(2))
        print("url found: {}".format(hist_url))
        return hist_url
    else:
        print("Game not found =(")
        return None


def find_min_price_by_url(url):
    df = get_dataframes_by_url(url)
    df = process_dataframe(df)
    return df


def find_min_price_by_game(game):
    hist_url = find_history_url(game)
    return find_min_price_by_url(hist_url)


@command()
@option(
    "--game",
    default=None,
    help="Name of the game that the minimum price is wanted. TYPE THE SAME as it appears on boardgameprices.co.uk"
)
@option(
    "--url",
    default=None,
    help="Direct url to history page of the desided game on boardgameprices.co.uk.\nThis have priority over --game option"
)
def main(
    url=None,
    game=None
):
    """Finds the lowest price from game's history on boardgameprices.co.uk.
    """
    if url==None:
        if game==None:
            print("Usage: run with an url to the desired game's history or a game name.")
        else:
            result = find_min_price_by_game(game)
            print_lowest_game_price(game,result)

    else:
        result = find_min_price_by_url(url)
        print_lowest_price(result)


if __name__ == "__main__":
    main()
