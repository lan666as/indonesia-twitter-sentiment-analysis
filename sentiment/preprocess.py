import pandas as pd
import nltk
import re

alay_dict = pd.read_csv('lexicon/slang-words.csv', encoding='latin-1', header=None)
alay_dict = alay_dict.rename(columns={0: 'original', 
                                      1: 'replacement'})
alay_dict_map = dict(zip(alay_dict['original'], alay_dict['replacement']))

def preprocess_tweet(text):
  text = re.sub(r'RT @\w+:', ' ', text) # Remove RT symbol
  text = re.sub('\n',' ',text) # Remove every '\n'
  text = re.sub(r'\@\w+',' ',text) # Remove every username
  text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text) # Remove every URL
  text = re.sub('/', ' ', text) # separate or (/)
  text = re.sub('  +', ' ', text) # Remove extra spaces
  text = text.strip() # strip
  return text

def explode_hashtag(text):
  text = re.sub(r'(?<![A-Z\W])(?=[A-Z])', ' ', text) # split at uppercase letter 
  text = re.sub('#', ' ', text) # remove hashtag #
  return text

def normalize_alay(text):
  def preserve_case(word, replacement):
    if word.islower(): return replacement.lower()
    if word.istitle(): return replacement.title()
    if word.isupper():
      if (len(word.split()) == len(replacement.split())):
        return replacement.upper()
      else:
        return replacement.title()
      
    else: return replacement

  return ' '.join([preserve_case(word, alay_dict_map[word.lower()]) if word.lower() in alay_dict_map else word for word in text.split(' ')])

def preprocess(text):
    text = preprocess_tweet(text)
    text = explode_hashtag(text)
    text = normalize_alay(text)

    return text