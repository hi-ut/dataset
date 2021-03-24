import sys
import bs4
import hashlib
import json
import bs4
import requests
import time
import os
import urllib.parse
import csv
import glob
from rdflib import URIRef, BNode, Literal, Graph
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from rdflib import Namespace
import pandas as pd
import uuid
import bs4
import hashlib

prefix0 = "https://hi-nishikie.web.app"
static_dir = "../../static"

files = glob.glob(static_dir + "/api/iiif/collection/*.json")

collections = []

for file in files:
    print(file)

    if "top.json" in file:
        continue

    json_open = open(file, 'r')
    df = json.load(json_open)

    del df["manifests"]
    del df["@context"]

    collections.append(df)

collection = {
    "@context": "http://iiif.io/api/presentation/2/context.json",
    "@id": prefix0 + "/api/iiif/collection/top.json",
    "label" : "錦絵ギャラリー",
    "@type": "sc:Collection",
    "collections": collections,
}

f_path = collection["@id"].replace(prefix0, static_dir)
with open(f_path, 'w') as outfile:
    json.dump(collection, outfile, ensure_ascii=False,
                indent=4, sort_keys=True, separators=(',', ': '))