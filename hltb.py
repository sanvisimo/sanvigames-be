import requests
from bs4 import BeautifulSoup
import re


def hltb(url):
    page = requests.get(url, headers={"User-Agent": "AugmentedSteam/1.0 (+bots@isthereanydeal.com)"})
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find_all(text=re.compile('Rating'))
    return results[0].replace('% Rating', '') if results[0] != 'NR Rating' else None


if __name__ == "__main__":
    import sys

    hltb(sys.argv[1])
