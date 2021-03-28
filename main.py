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

while(i<=totalNumberOfDocuments):
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

def isValidOperator(__operatorList):
  check = True

  for operator in __operatorList:
    if (isOperatorOR(operator) or isOperatorAND(operator)):
      check = check and True
    else:
      check = check and False

  return (check)


def isOperatorNOT(__operator):
  if (__operator == 'not'):
    return (True)
  return (False)

def isOperatorAND(__operator):
  if (__operator == 'and'):
    return (True)
  return (False)

def isOperatorOR(__operator):
  if (__operator == 'or'):
    return (True)
  return (False)

def singleTermQuery(__term):
  __term = __term.lower()
  stemmedTerm = stemmer.stem(__term)

  documents = []

  for document in dictionary[stemmedTerm]:
    documents.append(document)

  return (documents)

def ORQuery(__firstTermDocuments, __secondTermDocuments):
  totalDocuments = []
  i = 0
  j = 0

  while(i < len(__firstTermDocuments) and j < len(__secondTermDocuments)):
    if(__firstTermDocuments[i] == __secondTermDocuments[j]):
      totalDocuments.append(__firstTermDocuments[i])
      i += 1
      j += 1
    elif(__firstTermDocuments[i] < __secondTermDocuments[j]):
      totalDocuments.append(__firstTermDocuments[i])
      i += 1
    else:
      totalDocuments.append(__secondTermDocuments[j])
      j += 1

  while (i < len(__firstTermDocuments)):
    totalDocuments.append(__firstTermDocuments[i])
    i += 1

  while (j < len(__secondTermDocuments)):
    totalDocuments.append(__secondTermDocuments[j])
    j += 1


  return (totalDocuments)
  
def ANDQuery(__firstTermDocuments, __secondTermDocuments):
  totalDocuments = []
  i = 0
  j = 0
  
  while(i < len(__firstTermDocuments) and j < len(__secondTermDocuments)):
    if (__firstTermDocuments[i] == __secondTermDocuments[j]):
      totalDocuments.append(__firstTermDocuments[i])
      i += 1
      j += 1
    elif (__firstTermDocuments[i] < __secondTermDocuments[j]):
      i += 1
    else:
      j += 1

  return (totalDocuments)

def NOTQuery(__termDocuments):
  totalDocs = list(range(1, totalNumberOfDocuments + 1))
  requiredDocs = []
  i = 0
  j = 0

  while(i < len(totalDocs) and j < len(__termDocuments)):
    if (totalDocs[i] == __termDocuments[j]):
      i += 1
      j += 1
    elif (totalDocs[i] < __termDocuments[j]):
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

  if (len(__documents) == 0):
    print('None retrieved')
  else:
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
  elif (len(parsedQuery) == 2 and isOperatorNOT(parsedQuery[0])):
    documents = NOTQuery(singleTermQuery(parsedQuery[1]))
  elif (len(parsedQuery) == 3 and isValidOperator([ parsedQuery[1] ])):
    documents = twoTermQuery(singleTermQuery(parsedQuery[0]), singleTermQuery(parsedQuery[2]), parsedQuery[1])
  elif (len(parsedQuery) == 4 and (isOperatorNOT(parsedQuery[0]) or isOperatorNOT(parsedQuery[2]))):
    if (isOperatorNOT(parsedQuery[0])):
      documents = twoTermQuery(NOTQuery(singleTermQuery(parsedQuery[1])), singleTermQuery(parsedQuery[3]), parsedQuery[2])
    else:
      documents = twoTermQuery(singleTermQuery(parsedQuery[0]), NOTQuery(singleTermQuery(parsedQuery[3])), parsedQuery[1])
  elif (len(parsedQuery) == 5 and isValidOperator([ parsedQuery[1], parsedQuery[3] ])):
    documents = twoTermQuery(twoTermQuery(singleTermQuery(parsedQuery[0]), singleTermQuery(parsedQuery[2]), parsedQuery[1]), singleTermQuery(parsedQuery[4]), parsedQuery[3])
  elif (len(parsedQuery) == 5 and isOperatorNOT(parsedQuery[0]) and isOperatorNOT(parsedQuery[3])):
    documents = twoTermQuery(NOTQuery(singleTermQuery(parsedQuery[1])), NOTQuery(singleTermQuery(parsedQuery[4])), parsedQuery[2])
  printDocuments(documents)

# executeQuery('not strange and not play')

print(dictionary)
