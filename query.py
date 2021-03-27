import nltk
import re

totalNumberOfDocuments = 50

# Read and parse all stop words from file
fp = open('./Stopword-List.txt','r')
stopWords = fp.read()
stopWords = nltk.word_tokenize(stopWords)
fp.close()

stemmer = nltk.stem.porter.PorterStemmer()
punctuationRegex = "[.,!?:;‘’”“\"]"
dictionary = {}
i = 1

while(i<=45):
  fp = open('./ShortStories/{}.txt'.format(i), 'r')
  text = fp.read().lower()
  text = re.sub(punctuationRegex, "", text)
  text = nltk.word_tokenize(text)

  parsedItemsWithoutStopWords = []

  for item in text:
    item = stemmer.stem(item)
    if (not (item in stopWords)):
      parsedItemsWithoutStopWords.append(item)
  
  for index, item in enumerate(parsedItemsWithoutStopWords):
    if(not (item in dictionary)):
        dictionary[item] = {i: [index]}
    else:
      if(not (i in dictionary[item])):
        dictionary[item][i] = [index]
      else:
        dictionary[item][i].append(index)

  i += 1

def singleTermQuery(__term):
  __term = __term.lower()
  stemmedTerm = stemmer.stem(__term)
  return (dictionary[stemmedTerm])

def ORQuery(__firstTerm, __secondTerm):
  firstTermDocuments = []
  secondTermDocuments = []

  for document in singleTermQuery(__firstTerm):
    firstTermDocuments.append(document)

  for document in singleTermQuery(__secondTerm):
    secondTermDocuments.append(document)

  totalDocuments = []
  i = 0
  j = 0

  while(i < len(firstTermDocuments) and j < len(secondTermDocuments)):
    if(firstTermDocuments[i] == secondTermDocuments[j]):
      totalDocuments.append(firstTermDocuments[i])
      i += 1
      j += 1
    elif(firstTermDocuments[i] < secondTermDocuments[j]):
      totalDocuments.append(firstTermDocuments[i])
      i += 1
    else:
      totalDocuments.append(secondTermDocuments[j])
      j += 1

  while (i < len(firstTermDocuments)):
    totalDocuments.append(firstTermDocuments[i])
    i += 1

  while (j < len(secondTermDocuments)):
    totalDocuments.append(secondTermDocuments[j])
    j += 1


  return (totalDocuments)
  
def ANDQuery(__firstTerm, __secondTerm):
  firstTermDocuments = []
  secondTermDocuments = []

  for document in singleTermQuery(__firstTerm):
    firstTermDocuments.append(document)

  for document in singleTermQuery(__secondTerm):
    secondTermDocuments.append(document)

  totalDocuments = []
  i = 0
  j = 0
  
  while(i < len(firstTermDocuments) and j < len(secondTermDocuments)):
    if (firstTermDocuments[i] == secondTermDocuments[j]):
      totalDocuments.append(firstTermDocuments[i])
      i += 1
      j += 1
    elif (firstTermDocuments[i] < secondTermDocuments[j]):
      i += 1
    else:
      j += 1

  return (totalDocuments)

def NOTQuery(__termDocuments):
  totalDocs = list(range(1, totalNumberOfDocuments + 1))
  termDocs = []
  
  for document in __termDocuments:
    termDocs.append(document)

  requiredDocs = []
  i = 0
  j = 0

  while(i < len(totalDocs) and j < len(termDocs)):
    if (totalDocs[i] == termDocs[j]):
      i += 1
      j += 1
    elif (totalDocs[i] < termDocs[j]):
      requiredDocs.append(totalDocs[i])
      i += 1
    else:
      j += 1
  
  while(i < len(totalDocs)):
    requiredDocs.append(totalDocs[i])
    i += 1

  return (requiredDocs)

def printDocuments(__documents):
  print("Documents:", end=' ')
  for document in __documents:
    print(document, end=',')

def twoTermQuery(__firstTermDocuments, __secondTermDocuments, __operator):
  if (__operator == 'and'):
    return (ANDQuery(__firstTermDocuments, __secondTermDocuments))
  elif (__operator == 'or'):
    return (ORQuery(__firstTermDocuments, __secondTermDocuments))

def executeQuery(__query):
  parsedQuery = nltk.word_tokenize(__query)
  documents = []

  if (len(parsedQuery) == 1):
    documents = singleTermQuery(parsedQuery[0])
  elif (len(parsedQuery) == 2 and parsedQuery[0] == 'not'):
    documents = NOTQuery(singleTermQuery(parsedQuery[1]))
  elif (len(parsedQuery) == 3):
    documents = twoTermQuery(parsedQuery[0], parsedQuery[2], parsedQuery[1])
  elif (len(parsedQuery) == 5):
    pass
  
  printDocuments(documents)

executeQuery('power or play')

# print(dictionary)
