#!/usr/bin/python3

from click import command, option
import numpy as np
import pandas as pd
import re
from requests import get


NEW_PRICE_PATTERN = r"([0-9]+.[0-9]+) \+ shipping"


def find_price(str):
    matchObj = re.search(NEW_PRICE_PATTERN, str)
    if matchObj:
        return float(matchObj.group(1))
    else:
        return np.nan


def create_dataframe_from_url(url):
    data = pd.read_html(url)
    df = data[0]
    df["Price"] = df['Event'].apply(lambda x: find_price(x))
    df.dropna().head()
    df['Date'] = pd.to_datetime(df['Date'])
    return df


def print_minimum_price(df):
    print("The min price was £{} on {} at {}".format(df['Price'].min(),df[df['Price']==df['Price'].min()]['Date'].to_string(index=False),df[df['Price']==df['Price'].min()]['Store'].to_string(index=False)))


def find_min_price_by_url(url):
    df = create_dataframe_from_url(url)
    print(print_minimum_price(df))


def generate_pattern(game):
    return r"<a href=\"/item/show/([0-9]+)/(.*)\">"+game+"</a>"


def find_history_url(game):
    pattern = generate_pattern(game)
    url = "https://boardgameprices.co.uk/item/search?search="+game
    response = get(url)
    matchObj = re.search(pattern,response.text)
    if matchObj:
        hist_url = "https://boardgameprices.co.uk/item/history/{}/{}".format(matchObj.group(1),matchObj.group(2))
        return hist_url
    else:
        print("Game not found =(")
        return None


def find_min_price_by_game(game):
    hist_url = find_history_url(game)
    df = create_dataframe_from_url(hist_url)
    print(print_minimum_price(df))


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
            find_min_price_by_game(game)
    else:
        find_min_price_by_url(url)


if __name__ == "__main__":
    main()
