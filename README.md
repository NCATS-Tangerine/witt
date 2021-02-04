# witt

* Uses [SpaCy](https://spacy.io/) to parse a list of questions.
* Does named entity recognition (NER) with a few tools.
* Outputs all resulting metadata to YAML in the data subdirectory.

```
$ python3.8 -m venv <env>
$ source <env>/bin/activate
$ pip install -r requirements.txt
$ mkdir data
$ python parser.py
```  
