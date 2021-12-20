import csv
import os

import requests as r
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

BASE = "https://www.manualslib.com"
DOMAIN = "https://www.manualslib.com/brand/grundfos/"
PATH_TO_NAMES = os.path.abspath(os.curdir) + "/products.csv"


def get_href_for_categories(domain):
    links = set()
    page = r.get(domain)
    soup = bs(page.content, "html.parser")
    containers = soup.find_all("div", {"class": "cathead"})
    pbar = tqdm(total=len(containers))
    pbar.set_description("Getting product categories")
    for con in containers:
        links.add(f"{BASE}{con.find('a')['href']}")
        pbar.update(1)
    pbar.close()
    return links


def get_product_names(containerHref):
    names = set()
    pbar = tqdm(total=len(containerHref))
    pbar.set_description("Getting product names")
    for c in containerHref:
        splitDomain = c.split("/")[5].replace(".html", "").replace("-", " ")
        page = r.get(c)
        soup = bs(page.content, "html.parser")
        containers = soup.find_all("div", {"class": "col-sm-2 mname"})
        for cn in containers:
            try:
                text = cn.find("a").text
                names.add((text, splitDomain))
            except:
                continue
        pbar.update(1)
    pbar.close()
    return names


def save_names_to_list(names, path):
    with open(path, "w", newline="") as out:
        csv_out = csv.writer(out)
        csv_out.writerow(["Name", "Tag"])
        for row in names:
            print(row)
            csv_out.writerow(row)


"""
    pbar = tqdm(total=1)
    pbar.set_description("Saving product names")
    file = open(path, "w")
    file.writelines(names)
    file.close()
    pbar.update(1)
    pbar.close()"""


if __name__ == "__main__":
    links = get_href_for_categories(DOMAIN)
    names = get_product_names(links)
    save_names_to_list(names, PATH_TO_NAMES)
