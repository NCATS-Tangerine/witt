import requests
import json
import os

import spacy
import en_core_web_sm
nlp = en_core_web_sm.load()

nlp = spacy.load("en_core_web_sm")
doc = nlp("Apple is looking at buying U.K. startup for $1 billion")
for token in doc:
    print(token.text, token.pos_, token.dep_)

automat = "http://automat.renci.org/biolink/query"
aragorn = "https://aragorn-ranker.renci.org/score?jaccard_like=false"
strider = "http://robokop.renci.org:5781/query"

aras = [ automat, aragorn, strider ]

class Go:
    
    def fetch (self, message, url):        
        response = requests.post (
            url = url,
            json = message)
        if response.status_code != 200:
            print (f"{url} - status: {response.status_code}")
            #raise ValueError (f"broken request: {response.status_code}")
        return response.json ()

    def fetch_multiple (self, message):
        for ara in aras:
            response = self.fetch (message, ara)
            print (json.dumps(response, indent=2))
            
def main ():
    with open ("query.json", "r") as stream:
        request = json.load (stream)
        go = Go ()
        response = go.fetch_multiple (request)
        print (json.dumps(response, indent=2))

        response = go.fetch_multiple (request)
        print (json.dumps(response, indent=2))

if __name__ == '__main__':
    main ()
    
