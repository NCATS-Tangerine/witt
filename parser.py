import json
import os
import spacy
import requests
import yaml
import sys
from Levenshtein import distance 
from output import OutputStrategy, TableOutputStrategy, YAMLOutputStrategy

class Parser:
    def __init__(self):
        self.nlp = spacy.load ("en_core_web_sm")

    def parse (self, text):
        """
        1. Parse text into tokens with spacy.
        2. Include Translator appropriate identifiers via a lookup of noun tokens.
        This is simplistic and nowhere near as sophisticated as proper NER.
        Still, it picks up somme useful info.
        3. Parse entities with spacy. Docs suggest this wil require a purpose built model to 
        get reasonable results for our domain.
        4. Include the Biolink API NER results.
        """
        
        doc = self.nlp (text)
        tokens = [
            {
                "token" : token.text,
                "lemma" : token.lemma_,
                "pos"   : token.pos_,
                "tag"   : token.tag_,
                "dep"   : token.dep_,
                "shape" : token.shape_,
                "alpha" : token.is_alpha,
                "stop"  : token.is_stop,
                "sri"   : Semantic.lookup (token.text) if token.pos_ == 'NOUN' else None
            } for token in doc ]
        entities = [
            {
                "text"       : ent.text,
                "start_char" : ent.start_char,
                "end_char"   : ent.end_char,
                "label"      : ent.label
            } for ent in doc.ents ]
        return {
            "text"     : text,
            "bl_parse" : Semantic.biolink_lookup (text),
            "parse" : {
                "tok" : tokens,
                "ent" : entities 
            }
        }

    def parse_corpus (self, sentences):
        return [
            self.parse (sentence) for sentence in [
                s.strip() for s in sentences
            ]
        ]
    
class Semantic:
    
    @staticmethod
    def lookup (name):
        response = requests.post (
            url=f"http://robokop.renci.org:2433/lookup?string={name}&limit=10")
        if response.status_code == 200:
            response = response.json ()
        else:
            print (f"ERROR: {response.status_code} {response.text}")
            response = {}
        return {
            "full" : response,
            "min"  : next(iter(response)) if len(response) > 0 else None
        }
    
    @staticmethod
    def biolink_lookup (sentence):
        response = requests.post (
            url=f"https://api.monarchinitiative.org/api/nlp/annotate/entities?content={sentence}").json ()
        return response
    
    @staticmethod
    def normalize (i):
        response = requests.post (
            url=f"https://nodenormalization-sri.renci.org/get_normalized_nodes?curie={i}").json ()
        return response

    @staticmethod
    def get_biolink ():
        text = requests.get ("https://raw.githubusercontent.com/biolink/biolink-model/master/biolink-model.yaml").text
        return yaml.load (text)

    @staticmethod
    def get_biolink_relations ():
        model = Semantic.get_biolink ()
        for k, v in model.get ("types", {}).items ():
            print (v)
            if v.get('is_a',None) == 'related to':
                print (f"----> {v}")
        return [
            k for k, v in model.get ("slots", {}).items ()
            if v.get('is_a',None) == 'related to'
        ]
    
def main ():
    parser = Parser ()
    output = YAMLOutputStrategy ()
    with open ("questions.txt", "r") as stream:
        sentences = [ s.strip () for s in stream.readlines () ]
        for index, text in enumerate (sentences):
            if not output.is_written (index):
                sentence = parser.parse (text)
                output.write (index, sentence)

if __name__ == '__main__':
    main ()
    







    
def broken ():

    """ Get Biolink Model associations and poke around in the sentence looking for these. """
    relations = Semantic.get_biolink_relations ()
    print ("\n".join (relations))
    with open ("questions.txt", "r") as stream:
        sentences = [ s.strip ().split () for s in stream.readlines () ]
        for s in sentences:            
            blocks = []  # this will be for the consecutive subwords
            for block_size in range(1, len(s)):
                for i in range(len(s) - block_size + 1):
                    block = " ".join(s[i:(i + block_size)])
                    blocks.append(block)
            for block in blocks:
                for r in relations:
                    phrase = " ".join(block)
                    if len(phrase) > 4 and distance (phrase, r) < 4:
                        print (f"------> {block}")

            #print (blocks)
            
    sys.exit (0)
    
