import json
import yaml
import os

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
            token['sri']['min'] if token['sri']['min'] is not None else "" ))

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
    def __init__ (self, data_dir="data"):
        self.data_dir = data_dir
    def is_written (self, index):
        return os.path.exists (self.form_path (f"{index}-spacy-sri.csv"))
    def form_path (self, name):
        return os.path.join (self.data_dir, name)
    def write (self, index, sentence):
        print (f">> {sentence['text']} ... writing tables.")
        with open (self.form_path(f"{index}-spacy-sri.csv"), "w") as out:
            out.write (",".join ([ "TEXT", "LEMMA", "POS", "TAG", "DEP", "SHAPE", "ALPHA", "STOP", "ID" ]))
            out.write ("\n")
            for token in sentence['parse']['tok']:
                if token['token'] == '\n':
                    continue
                out.write (",".join ([
                    token['token'], token['lemma'], token['pos'], token['tag'], token['dep'],
                    token['shape'], str(token['alpha']), str(token['stop']),
                    token['sri']['min'] if token['sri']['min'] is not None else "" ]))
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
                
class YAMLOutputStrategy:    
    def __init__ (self, data_dir="data"):
        self.data_dir = data_dir
    def is_written (self, index):
        return os.path.exists (self.form_path (f"{index}.yaml"))
    def form_path (self, name):
        return os.path.join (self.data_dir, name)
    def write (self, index, sentence):
        print (f">> {sentence['text']} ... writing yaml.")
        with open (self.form_path(f"{index}.yaml"), "w") as stream:
            yaml.dump ({                       
                "question" : sentence['text'],
                "tokens"   : sentence['parse']['tok'],
                "ent"      : sentence['parse']['ent'],
                "bio_api"  : sentence['bl_parse']['spans']
            }, stream)


