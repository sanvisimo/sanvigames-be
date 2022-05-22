import requests
from bs4 import BeautifulSoup
import re
from howlongtobeatpy import HowLongToBeat


def hltb(url):
    page = requests.get(url, headers={"User-Agent": "AugmentedSteam/1.0 (+bots@isthereanydeal.com)"})
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find_all(text=re.compile('Rating'))
    print(results)
    return results[0].replace('% Rating', '') if results[0] != 'NR Rating' else None


def hltb_bak(game):
    url = 'https://howlongtobeat.com/search_results?page=1'
    data = {
        "queryString": game,
        "t": "games",
        "sorthead": "popular",
        "sortd": "0",
        "plat": "PC",
        "length_type": "main",
        "length_min": "",
        "length_max": "",
        "v": "",
        "f": "",
        "g": "",
        "detail": "",
        "randomize": "0",
    }

    page = requests.post(url, data, headers={"User-Agent": "AugmentedSteam/1.0 (+bots@isthereanydeal.com)"})
    print(page)
    return page


def get_howlongtobeat_infos(search):
    print('howlong')
    result = HowLongToBeat().search(search)
    if result:
        print(result)
        print('howlong end')
        return {
            "howlongtobeat_url": result[0].game_web_link,
            "howlongtobeat_main": float(str(result[0].gameplay_main).replace("½", ".5")),
            "howlongtobeat_main_unit": result[0].gameplay_main_unit,
            "howlongtobeat_main_extra": float(str(result[0].gameplay_main_extra).replace("½", ".5")),
            "howlongtobeat_main_extra_unit": result[0].gameplay_main_extra_unit,
            "howlongtobeat_completionist": float(str(result[0].gameplay_completionist).replace("½", ".5")),
            "howlongtobeat_completionist_unit": result[0].gameplay_completionist_unit,
        }
    print('no howlong')
    return None


if __name__ == "__main__":
    import sys

    get_howlongtobeat_infos(sys.argv[1])
