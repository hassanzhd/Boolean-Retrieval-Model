import nltk
import re

class BooleanRetrievalModel: # helper class implementing the model
  def __init__(self):
    self.totalNumberOfDocuments = 50
    self.stopWords = None
    self.dictionary = {}
    self.stemmer = nltk.stem.porter.PorterStemmer()
    self.invertedIndexFileName = "./index.txt"
    self.stopWordFileName = "./Stopword-List.txt"
    self.documentsPath = "./ShortStories/{}.txt"
    self.readInvertedIndexOrPreprocess()

  """ returns stop words  """
  def getStopWordsFromFile(self): 
    fp = open(self.stopWordFileName,'r')
    stopWords = fp.read()
    stopWords = nltk.word_tokenize(stopWords) # converting text to list of tokens
    fp.close()
    return (stopWords)

  """ returns all normalized tokens of document """
  def getTokensFromFile(self, __fileName):
    punctuationRegex = "[.,!?:;‘’”“\"]"
    fp = open(__fileName, 'r')
    text = fp.read().lower()  # case folding
    text = re.sub(punctuationRegex, "", text) # removal of punctuatiom
    text = re.sub("[-]", " ", text)
    tokens = nltk.word_tokenize(text) # converting text to list of tokens
    fp.close()
    return (tokens)

  """ creates inverted index containing all terms of documents """
  def createInvertedIndex(self):
    currentDocument = 1
    self.stopWords = self.getStopWordsFromFile()

    while(currentDocument<=self.totalNumberOfDocuments):
      fileTokens = self.getTokensFromFile(self.documentsPath.format(currentDocument))

      for position, word in enumerate(fileTokens):
        word = self.stemmer.stem(word)
        if (not (word in self.stopWords)):
          if(not (word in self.dictionary)):
              # adds 'word' to dictionary if not present and maps 'currentDocument' and 'position' as value to it
              self.dictionary[word] = {currentDocument: [position]} 
          else:
            if(not (currentDocument in self.dictionary[word])):
              # adds 'currentDocument' and 'position' to existing document dictionary of word
              self.dictionary[word][currentDocument] = [position]
            else:
              # appends postional index of 'currentDocument' for 'word'
              self.dictionary[word][currentDocument].append(position)

      currentDocument += 1

  """ writes inverted index to index.txt """
  def writeInvertedIndex(self):
    fp = open(self.invertedIndexFileName, 'w')
    fp.write(str(self.dictionary))
    fp.close()

  """ reads invertedIndex if index.txt exists otherwise creates and writes invertedIndex"""
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

  """ performs single term query by returning documents of it """
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

  """ performs a boolean operation on two documents lists provided using __opeartor """
  def twoTermQuery(self, __firstTermDocuments, __secondTermDocuments, __operator):
    if (__operator == 'and'):
      return (self.ANDQuery(__firstTermDocuments, __secondTermDocuments))
    elif (__operator == 'or'):
      return (self.ORQuery(__firstTermDocuments, __secondTermDocuments))

  """ returns documents depending on its type (actual/ not) """
  def getDocuments(self, __term):
    termValue = __term[0]
    typeOfQuery = __term[1]

    if(typeOfQuery == 'not'):
      return (self.NOTQuery(self.singleTermQuery(termValue)))
    return (self.singleTermQuery(termValue))

  """ returns posting list of __term using __documentID  """
  def getPostingList(self, __term, __documentID):
    __term = __term.lower()
    stemmedTerm = self.stemmer.stem(__term)
    return (self.dictionary.get(stemmedTerm).get(__documentID))

  def proximityQuery(self, __firstTerm, __secondTerm, __distance):
    totalDocuments = []
    i = 0
    j = 0

    while(i < len(__firstTerm[1]) and j < len(__secondTerm[1])):
        if (__firstTerm[1][i] == __secondTerm[1][j]):
          firstTermIndexes = self.getPostingList(__firstTerm[0], __firstTerm[1][i])
          secondTermIndexes = self.getPostingList(__secondTerm[0], __secondTerm[1][j])
          k = 0
          l = 0

          while(k < len(firstTermIndexes) and l < len(secondTermIndexes)):
            if (((secondTermIndexes[l] - 1) - firstTermIndexes[k] <= __distance) and ((secondTermIndexes[l] - 1) - firstTermIndexes[k] >= 0)):
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

  """ classifies terms of query into two types (actual/ not) and operators """
  def classifyTermsAndOperators(self, __parsedQuery):
    terms = []
    operators = []
    i = 0
    
    while (i < len(__parsedQuery)):
      if (__parsedQuery[i] == 'and' or __parsedQuery[i] == 'or'):
        operators.append(__parsedQuery[i])
        i += 1
      elif (__parsedQuery[i] == 'not'):
        terms.append((__parsedQuery[i + 1], 'not'))
        i += 2
      else:
        terms.append((__parsedQuery[i], 'actual'))
        i += 1
    
    return (terms, operators)

  """ returns documents of __terms """
  def getTermDocuments(self, __terms):
    i = 0
    termDocuments = []

    while(i < len(__terms)):
      termDocuments.append(self.getDocuments(__terms[i]))
      i += 1
    
    return (termDocuments)

  def executeQuery(self, __query):
    parsedQuery = nltk.word_tokenize(__query)
    documents = []

    if (len(parsedQuery) == 3 and self.isProximityQuery(parsedQuery[2])):
      documents = self.proximityQuery((parsedQuery[0], self.singleTermQuery(parsedQuery[0])),(parsedQuery[1], self.singleTermQuery(parsedQuery[1])),int(parsedQuery[2][1:]))
    else:
      i = 0
      terms, operators = self.classifyTermsAndOperators(parsedQuery)
      termDocuments = self.getTermDocuments(terms)

      while(len(operators) > 0):
        operator = operators.pop(0)
        firstTermDocuments = termDocuments.pop(0)
        secondTermDocuments = termDocuments.pop(0)
        termDocuments.insert(0, self.twoTermQuery(firstTermDocuments, secondTermDocuments, operator))
        i += 1

      documents = termDocuments[0]

    self.printDocuments(documents)

model = BooleanRetrievalModel()
model.executeQuery('ladies and gentleman')