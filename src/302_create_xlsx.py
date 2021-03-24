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

files = glob.glob("../docs/iiif/collection/*.json")

for file in files:
    print(file)

    json_open = open(file, 'r')
    df = json.load(json_open)

    items = df["collections"] if "collections" in df else df["manifests"]

    fields = ["Title"]

    data = []

    for item in items:
        

        map = {
            fields[0] : [item["label"]]
        }

        metadata = item["metadata"] if "metadata" in item else []

        for m in metadata:
            label = m["label"]
            value = m["value"]

            if label not in fields:
                fields.append(label)

            if label not in map:
                map[label] = []

            map[label].append(value)

        data.append(map)

    rows = []
    
    row = []
    rows.append(row)
    for i in range(len(fields)):
        row.append(fields[i])

    for item in data:
        row = []
        rows.append(row)

        for i in range(len(fields)):
            field = fields[i]

            value = ""
            if field in item:
                value = "|".join(item[field])

            row.append(value)

    df = pd.DataFrame(rows)

    df.to_excel(file.replace("collection", "metadata").replace(".json", ".xlsx"),
            index=False, header=False)