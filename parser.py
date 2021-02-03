import json
import os
import spacy
import requests

class Parser:
    def __init__(self):
        self.nlp = spacy.load ("en_core_web_sm")

    def parse (self, text):
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
                "sri_lu" : Semantic.lookup (token.text) if token.pos_ == 'NOUN' else None
            } for token in doc ]
        entities = [
            {
                "text"       : ent.text,
                "start_char" : ent.start_char,
                "end_char"   : ent.end_char,
                "label"  : ent.label
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
            url=f"http://robokop.renci.org:2433/lookup?string={name}&limit=10").json ()
        return next(iter(response)) if len(response) > 0 else None

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
        return yaml.load 

class OutputStrategy:
    def is_written (self, index):
        return False
    def write (self, index, sentence):
        print (f"\n>> {sentence['text']}")
        print ("SpaCy+SRI lookup:")
        fmt_str = "  {:<15} {:<15} {:<5} {:<5} {:<10} {:<15} {:<5} {:<5} {:<15}"
        print (fmt_str.format ("TEXT", "LEMMA", "POS", "TAG", "DEP", "SHAPE", "ALPHA", "STOP", "ID"))
        print ("  =======================================================================================")
        for token in sentence['parse']['tok']:
            if token['token'] == '\n':
                continue
            print (fmt_str.format (
                token['token'], token['lemma'], token['pos'], token['tag'], token['dep'],
                token['shape'], token['alpha'], token['stop'],
            token['sri_lu'] if token['sri_lu'] is not None else "" ))

        if len(sentence['parse']['ent']) > 0:
            ent_fmt_str = "  {:<40} {:<5} {:<5} {:<10}"
            print ("spaCy NER:")
            print (ent_fmt_str.format ("TEXT", "START_CH", "END_CH", "LABEL"))
            print ("  ===========================================================")
            for ent in sentence['parse']['ent']:
                print (ent_fmt_str.format (
                    ent['text'], ent['start_char'],
                    ent['end_char'], ent['label']))

        ent_fmt_str = "  {:<30} {:<30} {:<30} {:<5} {:<5}"
        print ("Biolink NER:")
        print (ent_fmt_str.format ("TEXT", "IDS", "CATEGORY", "START", "END"))
        print ("  =======================================================================================================")
        for bl_lookup in sentence['bl_parse']['spans']:
            token = bl_lookup['token'][0]
            categories = token['category']
            category = categories[0] if len(categories) > 0 else ""
            print (ent_fmt_str.format (
                bl_lookup['text'], token['id'],
                category,
                bl_lookup['start'], bl_lookup['end']))

class TableOutputStrategy:
    
    def is_written (self, index):
        return os.path.exists (self.form_path (f"{index}-spacy-sri.csv"))
    def __init__ (self, data_dir="data"):
        self.data_dir = data_dir
    def form_path (self, name):
        return os.path.join (self.data_dir, name)
    def write (self, index, sentence):
        print (f"\n>> {sentence['text']}")
        print (f"   ...writing tables.")

        with open (self.form_path(f"{index}-spacy-sri.csv"), "w") as out:
            out.write (",".join ([ "TEXT", "LEMMA", "POS", "TAG", "DEP", "SHAPE", "ALPHA", "STOP", "ID" ]))
            out.write ("\n")
            for token in sentence['parse']['tok']:
                if token['token'] == '\n':
                    continue
                out.write (",".join ([
                    token['token'], token['lemma'], token['pos'], token['tag'], token['dep'],
                    token['shape'], str(token['alpha']), str(token['stop']),
                    token['sri_lu'] if token['sri_lu'] is not None else "" ]))
                out.write ("\n")
        if len(sentence['parse']['ent']) > 0:
            with open (self.form_path(f"{index}-spacy-entity.csv"), "w") as ent_out:
                ent_out.write (",".join ([ "TEXT", "START_CH", "END_CH", "LABEL" ]))
                ent_out.write ("\n")
                for ent in sentence['parse']['ent']:
                    ent_out.write (",".join ([
                        ent['text'], str(ent['start_char']),
                        str(ent['end_char']), str(ent['label']) ]))
                    ent_out.write ("\n")
        with open (self.form_path(f"{index}-biolink-api-entity.csv"), "w") as bio_out:
            bio_out.write (",".join ([ "TEXT", "IDS", "CATEGORY", "START", "END" ]))
            bio_out.write ("\n")
            for bl_lookup in sentence['bl_parse']['spans']:
                token = bl_lookup['token'][0]
                categories = token['category']
                category = categories[0] if len(categories) > 0 else ""
                bio_out.write (",".join ([
                    bl_lookup['text'], token['id'],
                    category,
                    str(bl_lookup['start']), str(bl_lookup['end']) ]))
                bio_out.write ("\n")
def main ():
    parser = Parser ()
    output = TableOutputStrategy ()
    with open ("questions.txt", "r") as stream:
        sentences = [ s.strip () for s in stream.readlines () ]
        for index, text in enumerate (sentences):
            if not output.is_written (index):
                sentence = parser.parse (text)
                output.write (index, sentence)

if __name__ == '__main__':
    main ()
    
