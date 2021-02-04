# witt

* Uses [SpaCy](https://spacy.io/) to parse a list of questions.
* Does named entity recognition (NER) with a few tools including [Biolink API](https://api.monarchinitiative.org/api/)
* Outputs all resulting metadata to YAML in the data subdirectory.

```
$ python3.8 -m venv <env>
$ source <env>/bin/activate
$ pip install -r requirements.txt
$ mkdir data
$ python parser.py
```  
This will produce output like:
```
>> Is Hirschsprung disease a mendelian or a multifactorial disorder? ... writing yaml.
>> What is the aim of the Human Chromosome-centric Proteome Project (C-HPP)? ... writing yaml.
>> What is the effect of ivabradine in heart failure after myocardial infarction? ... writing yaml.
>> What is the effect of TRH on myocardial contractility? ... writing yaml.
>> What are the outcomes of Renal sympathetic denervation? ... writing yaml.
...
```

And files in the data directory.
