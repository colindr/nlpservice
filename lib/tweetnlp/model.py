
import logging
import os
import numpy
import json
from typing import Dict, Callable


logger = logging.getLogger(__name__)

# these are special words that we assume nobody is using in actual
# tweets.  There's probably a better actual way to do this, but
# for now this is fine.
STARTOFTWEET = 'startoftweet'
ENDOFTWEET = 'endoftweet'

MAX_TWEET_LENGTH = 280


def read_glove_file(glove_file: str) -> (Dict[str, int], Dict[int, str], Dict):
    with open(glove_file, 'r') as f:
        word_glove = {}  # map from a token (word) to a Glove embedding vector

        for line in f:
            record = line.strip().split()
            token = record[0]  # take the token (word) from the text line
            word_glove[token] = numpy.array(record[1:],
                                            # associate the Glove embedding vector to a that token (word)
                                            dtype=numpy.float64)

    return word_glove


def glove_file(embedding_dim: int = 25) -> str:
    path = f"glove/glove.twitter.27B.{embedding_dim}d.txt"
    return os.path.join(os.path.dirname(__file__), path)


def create_pretrained_embedding_matrix(word_glove, word_index: Dict[str, int], vocab_size: int, embedding_dim: int = 25) -> (int, numpy.array):

    embeddingMatrix = numpy.zeros((vocab_size, embedding_dim))  # initialize with zeros
    for word, index in word_index.items():
        if word in word_glove:
            embeddingMatrix[index, :] = word_glove[word]  # create embedding: word index to Glove word embedding

    # make sure we set the STARTOFTWEET and ENDOFTWEET values to be different
    embeddingMatrix[vocab_size - 1] = [0] * embedding_dim
    embeddingMatrix[vocab_size - 2] = [1] * embedding_dim

    return embeddingMatrix


def glove_embedding(vocab_size: int, embedding_dim: int, input_length: int, word_index: Dict[str, int]):
    import keras

    word_glove = read_glove_file(glove_file(embedding_dim))
    emb_matrix = create_pretrained_embedding_matrix(word_glove, word_index, vocab_size, embedding_dim)
    embedding = keras.layers.Embedding(vocab_size, embedding_dim, weights=[emb_matrix],
                                       input_length=input_length, trainable=False)

    return embedding


# this loads the tweets and
def build_tweet_model(tweet_text: str, model_file: str, tokenizer_file: str,
                      epochs: int = 50, embedding_dim: int = 25,
                      pre_trained_embedding: bool = False, stats_callback: Callable = None):
    import numpy
    import tensorflow
    import keras

    # not sure if these need to be the same
    numpy.random.seed(42)
    tensorflow.compat.v1.set_random_seed(42)

    # this was built from this tutorial:
    # https://machinelearningmastery.com/develop-word-based-neural-language-models-python-keras/
    with open(tweet_text, 'r') as fp:
        # each line is a tweet
        tweets = fp.readlines()
        # data is just all the words in the tweets
        data = ''
        for tweet in tweets:
            data += tweet.strip()

        data = data.strip()

    tokenizer = keras.preprocessing.text.Tokenizer()
    tokenizer.fit_on_texts([data])
    encoded_tweets = tokenizer.texts_to_sequences(tweets)

    vocab_size = len(tokenizer.word_index) + 3
    print('Vocabulary Size: %d' % vocab_size)

    word_index = tokenizer.word_index.copy()
    word_index[STARTOFTWEET] = vocab_size-1
    word_index[ENDOFTWEET] = vocab_size-2

    index_word = tokenizer.index_word.copy()
    index_word[vocab_size-1] = STARTOFTWEET
    index_word[vocab_size-2] = ENDOFTWEET

    # create word -> word sequences
    sequences = list()
    for tweet in encoded_tweets:
        if len(tweet) < 2:
            continue
        # start of tweet sequence
        sequences.append([word_index[STARTOFTWEET], word_index[STARTOFTWEET], tweet[0]])
        sequences.append([word_index[STARTOFTWEET], tweet[0], tweet[1]])
        # word -> next_word sequences
        for i in range(2, len(tweet)):
            sequences.append(tweet[i - 2:i + 1])

        # end of tweet sequence
        sequences.append([tweet[-2], tweet[-1], word_index[ENDOFTWEET]])
        sequences.append([tweet[-1], word_index[ENDOFTWEET], word_index[ENDOFTWEET]])

    print('Total Sequences: %d' % len(sequences))

    if pre_trained_embedding:
        embedding = glove_embedding(vocab_size, embedding_dim, 2, tokenizer.word_index)
    else:
        embedding = keras.layers.Embedding(vocab_size, embedding_dim, input_length=2)

    # x is the set of input words, y is the set of output words
    sequences = numpy.array(sequences)
    # x = sequences[:, 0]
    # y = sequences[:, 1]
    x, y = sequences[:, :-1], sequences[:, -1]

    # one hot encode outputs
    y = keras.utils.to_categorical(y, num_classes=vocab_size)

    # define model
    model = keras.models.Sequential()

    model.add(embedding)
    model.add(keras.layers.LSTM(50))
    model.add(keras.layers.core.Dense(vocab_size, activation='softmax'))
    print(model.summary())

    # compile network
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    # fit network
    model.fit(x, y, epochs=epochs, verbose=2)

    # save the model
    model.save(model_file)

    with open(tokenizer_file, 'w') as fp:
        fp.write(json.dumps([word_index, index_word]))


def tweet_from_model(model_file: str, tokenizer_file: str, pre_trained_embedding: bool = False, embedding_dim: int = 25):
    import keras
    word_index, index_word = get_predict_maps(tokenizer_file, pre_trained_embedding, embedding_dim)

    model = keras.models.load_model(model_file)

    return generate_tweet(model, word_index, index_word)


def get_predict_maps(tokenizer_file: str, pre_trained_embedding: bool, embedding_dim: int):
    import keras
    if pre_trained_embedding:
        word_index, index_word, _ = read_glove_file(glove_file(embedding_dim))
    else:
        with open(tokenizer_file, 'r') as fp:
            word_index, index_word = json.load(fp)

    # somehow these get str keys
    index_word = {int(k):v for k,v in index_word.items()}
    return word_index, index_word


# generate a sequence from the model
def generate_tweet(model, word_index, index_word):
    import numpy

    last_words = [STARTOFTWEET, STARTOFTWEET]
    length = 0
    tweet = []
    while True:
        encoded = numpy.array([[word_index.get(w, 0) for w in last_words]])
        # predict a word in the vocabulary
        yhat = model.predict_classes(encoded, verbose=0)[0]
        # map predicted word index to word
        next_word = index_word[yhat]
        logger.debug(f'got next word {next_word} from last words {last_words}')
        if next_word == ENDOFTWEET:
            break
        elif length + len(next_word) + 1 > MAX_TWEET_LENGTH:
            break

        tweet.append(next_word)
        length += 1 + len(next_word)
        last_words = [last_words[-1], next_word]

    return ' '.join(tweet)


def predict(model_file: str, tokenizer_file: str, pre_trained_embedding: bool = False, embedding_dim: int = 25):
    import keras
    import numpy

    word_index, index_word = get_predict_maps(tokenizer_file, pre_trained_embedding, embedding_dim)

    model = keras.models.load_model(model_file)

    def predict_one(last_words):
        encoded = numpy.array([[word_index.get(w, 0) for w in last_words]])
        # predict a word in the vocabulary
        yhat = model.predict_classes(encoded, verbose=0)[0]
        # map predicted word index to word
        next_word = index_word[yhat]
        logger.debug(f'got next word {next_word} from last words {last_words}')
        return next_word

    def draw_predictions(stdscr):
        k = 0
        cursor_x = 0
        cursor_y = 0
        last_words = [STARTOFTWEET, STARTOFTWEET]
        tweet_words = []
        word_in_progress = ""

        prediction = predict_one(last_words)

        # Clear and refresh the screen for a blank canvas
        stdscr.clear()
        stdscr.refresh()

        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        while True:
            # Initialization
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            stdscr.addstr(f"input: {word_in_progress}\n")
            stdscr.addstr(f"prediction: {prediction}\n")
            stdscr.addstr(f"tweet: {' '.join(tweet_words)}\n")

            k = stdscr.getch()
            if chr(k) in ["\n"]:
                if word_in_progress == "":
                    next_word = prediction
                else:
                    next_word = word_in_progress

                if next_word == 'endoftweet':
                    break

                last_words = [last_words[-1], next_word]
                tweet_words.append(next_word)
                word_in_progress = ""
                prediction = predict_one(last_words)

            elif chr(k) in [" "]:
                continue
            elif k == 127:
                if word_in_progress:
                    word_in_progress = word_in_progress[:-1]
            else:
                word_in_progress += chr(k)

        stdscr.clear()
        stdscr.addstr(f"tweet: {' '.join(tweet_words)}\n")
        # one more char for ending
        stdscr.getch()

    import curses
    try:
        curses.wrapper(draw_predictions)
    except KeyboardInterrupt:
        pass
