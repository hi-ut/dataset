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

files = glob.glob("data/*.html")
files = sorted(files)
from PIL import Image
import shutil

dirname = "nishikie_shizuoka"

prefix0 = "https://hi-ut.github.io/dataset"
static_dir = "../../../docs"

def download_img(url, file_name):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

for i in range(len(files)):
    file = files[i]
    if i % 100 == 0:
        print(i+1, len(files), file)

    if str(i+1) not in file:
        print(file)

    soup = bs4.BeautifulSoup(open(file), 'lxml')
    aas = soup.find_all("a")

    

    trs = soup.find(class_="dcon_tbl0").find_all("tr")

    metadata = []

    cn = "-1"
    label = ""

    for tr in trs:
        tds = tr.find_all("td")

        if len(tds) != 2:
            continue

        field = tds[0].text.replace("【", "").replace("】", "").strip()

        if field == "":
            continue

        value = tds[1].text.strip()

        if value == "":
            continue

        metadata.append({
            "label" : field,
            "value" : value
        })

        if field == "請求記号":
            cn = value

        if field == "題名":
            label = value


    prefix = prefix0 + "/iiif/{}-{}".format(dirname, str(i+1).zfill(4))

    manifest_uri = prefix + "/manifest.json"

    canvases = []

    index = 1

    thumbnail = None

    for i in range(len(aas)):
        # print(a)
        a = aas[len(aas) - i - 1]
        manifest = a.get("href")
        if manifest and "clioimg" in manifest:

            # print(manifest)

            manifest = manifest.replace("http://clioimg.hi.u-tokyo.ac.jp/EXT/nishikie/12000005/000000018.jpg", "http://clioimg.hi.u-tokyo.ac.jp/EXT/nishikie/12000005/00000018.jpg")

            uuid = hashlib.md5(manifest.encode('utf-8')).hexdigest()

            path = "images/{}.jpg".format(uuid)

            if not os.path.exists(path):
                download_img(manifest, path)

            try:

                im = Image.open(path)

                w, h = im.size

                canvas = prefix + "/canvas/p{}".format(index)

                canvases.append({
                    "@id": canvas,
                    "@type": "sc:Canvas",
                    "height": h,
                    "images": [
                        {
                            "@id": prefix+"/p{}-image".format(index),
                            "@type": "oa:Annotation",
                            "format": "image/jpeg",
                            "motivation": "sc:painting",
                            "on": canvas,
                            "resource": {
                                "@id": manifest,
                                "@type": "dctypes:Image",
                                "format": "image/jpeg",
                                "height": h,
                                "width": w
                            }
                        }
                    ],
                    "thumbnail": {
                        "@id": manifest,
                        "@type": "dctypes:Image",
                        "format": "image/jpeg",
                        "height": h,
                        "width": w
                    },
                    "label": "[{}]".format(index),
                    "width": w
                })

                if index == 1:
                    thumbnail = {
                        "@id": manifest,
                        "@type": "dctypes:Image",
                        "format": "image/jpeg",
                        "height": h,
                        "width": w
                    }

                index += 1

            except Exception as e:
                print(e)

    m_data = {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@id": manifest_uri,
        "@type": "sc:Manifest",
        "attribution": "東京大学史料編纂所",
        
        "label": label,
        "license": "https://www.hi.u-tokyo.ac.jp/tosho/shiryoriyo.html",
        "logo": "https://www.hi.u-tokyo.ac.jp/favicon.ico",
        "metadata": metadata,
        "sequences": [
            {
                "@id": prefix + "/sequence/normal",
                "@type": "sc:Sequence",
                "canvases": canvases
            }
        ],
        "viewingDirection": "right-to-left",
    }

    if thumbnail:
        m_data["thumbnail"] = thumbnail

    f_path = manifest_uri.replace(prefix0, static_dir)
    dirname2 = os.path.dirname(f_path)
    os.makedirs(dirname2, exist_ok=True)

    with open(f_path, 'w') as outfile:
        json.dump(m_data, outfile, ensure_ascii=False,
                indent=4, sort_keys=True, separators=(',', ': '))