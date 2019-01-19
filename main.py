import xml.etree.ElementTree as ET
from data import professor_ids
import requests
from itertools import groupby
import pystache
import pickle
import urllib.parse


def to_pubs(xml):
    for r in xml:
        authors = [a.text for a in r.findall(".//author")]

        if not authors:
            continue
        
        title = r.find(".//title").text
        year = int(r.find(".//year").text)
        
        bt = r.findall(".//booktitle")
        jr = r.findall(".//journal")

        venue = "Unknown"
        if bt:
            venue = bt[0].text

        if jr:
            venue = jr[0].text

        key = r[0].attrib["key"]
        
        yield {"title": title,
               "year": year,
               "authors": authors,
               "venue": venue,
               "key": key}

def get_pubs(dblp_id):
    root = requests.get('http://dblp.org/pid/' + dblp_id + '.xml').text
    root = ET.fromstring(root)
    author_name = root.findall("./person/author")[0].text

    pubs = root.findall("r")
    pubs = list(to_pubs(pubs))
    return {"author": author_name,
            "pubs": pubs}


def get_all_pubs():
    res = []
    authors = []
    
    for p in professor_ids:
        results = get_pubs(p)
        authors.append(results["author"])
        res.extend(results["pubs"])


    # remove dups
    all_pubs = dict()
    for p in res:
        all_pubs[p["key"]] = p

    res = list(all_pubs.values())
    
        
    res = sorted(res, key=lambda x: x["year"],
                 reverse=True)
    res = groupby(res, key=lambda x: x["year"])

    authors = set(authors)

    data = []
    for k, g in res:
        papers = []
        for paper in sorted(g, key=lambda x: x["authors"][0]):
            paper["authors"] = [{"name": x,
                                 "primary": x in authors}
                                for x in paper["authors"]]
            
            paper["search"] = "https://scholar.google.com/scholar?{}".format(
                urllib.parse.urlencode({"q": paper["title"]})
            )
            
            papers.append(paper)
            
        data.append({"year": k,
                     "papers": papers})
        
    return data
    

def render(data):
    with open("template.mustache", "r") as f:
        template = f.read()

    print(pystache.render(template, {"data": data}))


try:
    with open("cache.pickle", "rb") as f:
        data = pickle.load(f)
except FileNotFoundError:
    data = get_all_pubs()
    with open("cache.pickle", "wb") as f:
        pickle.dump(data, f)
        
render(data)

