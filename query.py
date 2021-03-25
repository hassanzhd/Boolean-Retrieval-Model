import nltk
import re

fp = open('./Stopword-List.txt','r')
stopWords = fp.read()
stopWords = nltk.word_tokenize(stopWords)
fp.close()

stemmer = nltk.stem.porter.PorterStemmer()
punctuationRegex = "[.,!?:;‘’”“\"]"
dictionary = {}
i=1

while(i<=45):
  fp = open('./ShortStories/{}.txt'.format(i), 'r')
  text = fp.read().lower()
  text = re.sub(punctuationRegex, "", text)
  text = nltk.word_tokenize(text)

  for index, item in enumerate(text):
    item = stemmer.stem(item)
    if (not (item in stopWords)):
      if(not (item in dictionary)):
        dictionary[item] = {i: [index]}
      else:
        if(not (i in dictionary[item])):
          dictionary[item][i] = [index]
        else:
          dictionary[item][i].append(index)
  i += 1


print(dictionary)
