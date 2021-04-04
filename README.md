# BOOLEAN RETRIEVAL MODEL

The following assignment implements "Boolean Retrieval Model" which supports simple boolean and complex boolean queries along with proximity queries.

#### DATA SET:

Data set provided comprised of 50 short stories each of which had to be parsed, normalized and stemmed in order to form an inverted index containing terms, posting lists and postional indices

#### All possible supported queries:

1. q1, not q1
2. q1, not q1 (and, or) q2, not q2
3. q1, not q1 (and, or) q2, not q2 (and, or) q3, not q3
4. q1 q2 /k (proximity)

#### [Sample queries](https://k180208-ir-assignment1.azurewebsites.net/static/SampleQueries.txt)

#### [Deployed model on Azure App Services](https://k180208-ir-assignment1.azurewebsites.net/)
