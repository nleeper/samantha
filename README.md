# samantha
Personal assistant built to help you with all the things.

## Environment creation
1) mkvirtualenv --no-site-packages samantha
2) workon samantha
3) pip install -U tornado
4) pip install -U requests
5) pip install rasa_nlu
6) pip install -U spacy
7) python -m spacy download en
8) pip install -U scikit-learn
9) pip install -U scipy
10) pip install python-crfsuite

## Training
`python training.py`