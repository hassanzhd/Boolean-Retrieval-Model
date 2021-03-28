import nltk
import re

class BooleanRetrievalModel:
  def __init__(self):
    self.totalNumberOfDocuments = 50
    self.stopWords = None
    self.dictionary = {}
    self.stemmer = nltk.stem.porter.PorterStemmer()
    self.invertedIndexFileName = "./index.txt"
    self.stopWordFileName = "./Stopword-List.txt"
    self.readInvertedIndexOrPreprocess()

  def createInvertedIndex(self):
    fp = open(self.stopWordFileName,'r')
    self.stopWords = fp.read()
    self.stopWords = nltk.word_tokenize(self.stopWords)
    fp.close()

    punctuationRegex = "[.,!?:;‘’”“\"]"
    i = 1

    while(i<=self.totalNumberOfDocuments):
      fp = open('./ShortStories/{}.txt'.format(i), 'r')
      text = fp.read().lower()
      text = re.sub(punctuationRegex, "", text)
      text = nltk.word_tokenize(text)

      parsedItemsWithoutStopWords = []

      for item in text:
        item = self.stemmer.stem(item)
        if (not (item in self.stopWords)):
          parsedItemsWithoutStopWords.append(item)

      for index, item in enumerate(parsedItemsWithoutStopWords):
        if(not (item in self.dictionary)):
            self.dictionary[item] = {i: [index]}
        else:
          if(not (i in self.dictionary[item])):
            self.dictionary[item][i] = [index]
          else:
            self.dictionary[item][i].append(index)

      i += 1

  def writeInvertedIndex(self):
    fp = open(self.invertedIndexFileName, 'w')
    fp.write(str(self.dictionary))
    fp.close()

  def readInvertedIndexOrPreprocess(self):
    try:
      fp = open(self.invertedIndexFileName, 'r')
      data = fp.read()
      self.dictionary = eval(data)
      fp.close()
    except FileNotFoundError:
      self.createInvertedIndex()
      self.writeInvertedIndex()

  def isOperatorNOT(self, __operator):
    if (__operator == 'not'):
      return (True)
    return (False)

  def singleTermQuery(self, __term):
    __term = __term.lower()
    stemmedTerm = self.stemmer.stem(__term)

    documents = []

    for document in self.dictionary[stemmedTerm]:
      documents.append(document)

    return (documents)

  def ORQuery(self, __firstTermDocuments, __secondTermDocuments):
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

  def ANDQuery(self, __firstTermDocuments, __secondTermDocuments):
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


  def NOTQuery(self, __termDocuments):
    totalDocs = list(range(1, self.totalNumberOfDocuments + 1))
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

  def printDocuments(self, __documents):
    print("Documents:", end=' ')

    if (len(__documents) == 0):
      print('None retrieved')
    else:
      for document in __documents:
        print(document, end=',')

  def twoTermQuery(self, __firstTermDocuments, __secondTermDocuments, __operator):
    if (__operator == 'and'):
      return (self.ANDQuery(__firstTermDocuments, __secondTermDocuments))
    elif (__operator == 'or'):
      return (self.ORQuery(__firstTermDocuments, __secondTermDocuments))

  def getDocuments(self, __term):
    termValue = __term[0]
    typeOfQuery = __term[1]

    if(typeOfQuery == 'not'):
      return (self.NOTQuery(self.singleTermQuery(termValue)))
    return (self.singleTermQuery(termValue))

  def getValueFromKey(self, __term, __key):
    __term = __term.lower()
    stemmedTerm = self.stemmer.stem(__term)
    return (self.dictionary.get(stemmedTerm).get(__key))

  def proximityQuery(self, __firstTerm, __secondTerm, __distance):
    totalDocuments = []
    i = 0
    j = 0

    while(i < len(__firstTerm[1]) and j < len(__secondTerm[1])):
        if (__firstTerm[1][i] == __secondTerm[1][j]):
          firstTermIndexes = self.getValueFromKey(__firstTerm[0], __firstTerm[1][i])
          secondTermIndexes = self.getValueFromKey(__secondTerm[0], __secondTerm[1][j])
          k = 0
          l = 0

          while(k < len(firstTermIndexes) and l < len(secondTermIndexes)):
            if (secondTermIndexes[l] - firstTermIndexes[k] == __distance):
              totalDocuments.append(__firstTerm[1][i])
              break
            elif (firstTermIndexes[k] < secondTermIndexes[l]):
              k += 1
            else:
              l += 1

          i += 1
          j += 1
        elif (__firstTerm[1][i] < __secondTerm[1][j]):
          i += 1
        else:
          j += 1

    return (totalDocuments)

  def isProximityQuery(self, __term):
    if(__term[0] == '/'):
      return (True)
    return (False)

  def executeQuery(self, __query):
    parsedQuery = nltk.word_tokenize(__query)
    documents = []

    if (len(parsedQuery) == 1):
      documents = self.singleTermQuery(parsedQuery[0])
    elif (len(parsedQuery) == 2 and self.isOperatorNOT(parsedQuery[0])):
      documents = self.NOTQuery(self.singleTermQuery(parsedQuery[1]))
    elif (len(parsedQuery) == 3 and self.isProximityQuery(parsedQuery[2])):
      documents = self.proximityQuery((parsedQuery[0], self.singleTermQuery(parsedQuery[0])),(parsedQuery[1], self.singleTermQuery(parsedQuery[1])),int(parsedQuery[2][1:]))
    else:
      terms = []
      operators = []
      i = 0

      while (i < len(parsedQuery)):
        if (parsedQuery[i] == 'and' or parsedQuery[i] == 'or'):
          operators.append(parsedQuery[i])
          i += 1
        elif (parsedQuery[i] == 'not'):
          terms.append((parsedQuery[i + 1], 'not'))
          i += 2
        else:
          terms.append((parsedQuery[i], 'actual'))
          i += 1
      
      termDocuments = []
      i = 0 

      while(i < len(terms)):
        termDocuments.append(self.getDocuments(terms[i]))
        i += 1

      i = 0

      while(len(operators) > 0):
        operator = operators.pop(0)
        firstTermDocuments = termDocuments.pop(0)
        secondTermDocuments = termDocuments.pop(0)
        termDocuments.insert(0, self.twoTermQuery(firstTermDocuments, secondTermDocuments, operator))
        i += 1

      documents = termDocuments[0]

    self.printDocuments(documents)

model = BooleanRetrievalModel()
model.executeQuery('smiling face /3')