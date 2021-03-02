import math
import nltk
import os
import re
import string
import sys

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = dict()

    for file in os.scandir(directory):
        if re.match("\w*.txt", file.name):
            with open(file, 'r') as f:
                content = f.read()
                files[file.name] = content
                f.close()

    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    tokens = nltk.word_tokenize(document)
    processed = []

    # fetch libraries of strings to ignore
    punctuation = [char for char in string.punctuation]
    stops = nltk.corpus.stopwords.words("english")

    ignore = punctuation + stops

    for i in range(len(tokens)):
        token = tokens[i].lower()
        if token not in ignore:
            processed.append(token)

    return processed


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # list doc occurrences by word
    word_doc_matches = dict()

    for doc in documents:
        for word in documents[doc]:
            if word in word_doc_matches:
                word_doc_matches[word].add(doc)
            else:
                word_doc_matches[word] = {doc}

    # calculate inverse document frequency
    idfs = dict()
    num_docs = len(documents)

    for word in word_doc_matches:
        idfs[word] = math.log(num_docs / len(word_doc_matches[word]))

    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """

    tf_idfs = dict()

    for file in files:
        # get term frequencies
        tfs = {s:0 for s in query}

        for word in files[file]:
            if word in tfs:
                tfs[word] += 1

        tf_idfs[file] = sum([tfs[s] * idfs[s] for s in tfs if s in idfs])

    return sorted(tf_idfs, key=tf_idfs.get, reverse=True)[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    rankings = dict()

    for sentence in sentences:
        idfs_sum = 0
        term_freq = 0
        unseen = query.copy()

        for word in sentences[sentence]:
            if word in query:
                term_freq += 1
                if word in unseen:
                    idfs_sum += idfs[word]
                    unseen.remove(word)

        term_density = term_freq / len(sentences[sentence])

        rankings[sentence] = idfs_sum, term_density

    top_n_ranked = sorted(rankings, key=rankings.get, reverse=True)[:n]

    return top_n_ranked


if __name__ == "__main__":
    main()
