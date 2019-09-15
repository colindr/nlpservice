
import logging

logger = logging.getLogger(__name__)

# these are special words that we assume nobody is using in actual
# tweets.  There's probably a better actual way to do this, but
# for now this is fine.
STARTOFTWEET = 'startoftweet'
ENDOFTWEET = 'endoftweet'

MAX_TWEET_LENGTH = 280


# this loads the tweets and
def build_tweet_model(tweet_text: str, model_file: str, token_map_file: str):
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
        data = f'{STARTOFTWEET} '
        for tweet in tweets:
            data += tweet.strip() + f' {ENDOFTWEET} {STARTOFTWEET} '

        data = data.strip() + f' {ENDOFTWEET}'

    tokenizer = keras.preprocessing.text.Tokenizer()
    tokenizer.fit_on_texts([data])
    encoded_tweets = tokenizer.texts_to_sequences(tweets)

    vocab_size = len(tokenizer.word_index) + 1
    print('Vocabulary Size: %d' % vocab_size)

    # create word -> word sequences
    sequences = list()
    for tweet in encoded_tweets:
        if len(tweet) < 2:
            continue
        # start of tweet sequence
        sequences.append([tokenizer.word_index[STARTOFTWEET], tokenizer.word_index[STARTOFTWEET], tweet[0]])
        sequences.append([tokenizer.word_index[STARTOFTWEET], tweet[0], tweet[1]])
        # word -> next_word sequences
        for i in range(2, len(tweet)):
            sequences.append(tweet[i-2:i+1])

        # end of tweet sequence
        sequences.append([tweet[-2], tweet[-1], tokenizer.word_index[ENDOFTWEET]])
        sequences.append([tweet[-1], tokenizer.word_index[ENDOFTWEET], tokenizer.word_index[ENDOFTWEET]])

    print('Total Sequences: %d' % len(sequences))

    # x is the set of input words, y is the set of output words
    sequences = numpy.array(sequences)
    # x = sequences[:, 0]
    # y = sequences[:, 1]
    x, y = sequences[:, :-1], sequences[:, -1]

    # one hot encode outputs
    y = keras.utils.to_categorical(y, num_classes=vocab_size)

    # define model
    model = keras.models.Sequential()
    model.add(keras.layers.Embedding(vocab_size, 100, input_length=2))
    model.add(keras.layers.LSTM(50))
    model.add(keras.layers.core.Dense(vocab_size, activation='softmax'))
    print(model.summary())

    # compile network
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    # fit network
    model.fit(x, y, epochs=50, verbose=2)

    # save the model
    model.save(model_file)

    with open(token_map_file, 'w') as fp:
        fp.write(tokenizer.to_json())


def tweet_from_model(model_file: str, tokenizer_file: str):
    import keras
    with open(tokenizer_file, 'r') as fp:
        tokenizer = keras.preprocessing.text.tokenizer_from_json(fp.read())

    model = keras.models.load_model(model_file)

    return generate_tweet(model, tokenizer)


# generate a sequence from the model
def generate_tweet(model, tokenizer):
    import numpy

    last_words = [STARTOFTWEET, STARTOFTWEET]
    length = 0
    tweet = []
    while True:
        encoded = numpy.array([[tokenizer.word_index[w] for w in last_words]])
        # predict a word in the vocabulary
        yhat = model.predict_classes(encoded, verbose=0)[0]
        # map predicted word index to word
        next_word = tokenizer.index_word[yhat]
        logger.debug(f'got next word {next_word} from last words {last_words}')
        if next_word == ENDOFTWEET:
            break
        elif length + len(next_word) + 1 > MAX_TWEET_LENGTH:
            break

        tweet.append(next_word)
        length += 1 + len(next_word)
        last_words = [last_words[-1], next_word]

    return ' '.join(tweet)


def predict(model_file: str, tokenizer_file: str):
    import keras
    import numpy

    with open(tokenizer_file, 'r') as fp:
        tokenizer = keras.preprocessing.text.tokenizer_from_json(fp.read())

    model = keras.models.load_model(model_file)

    def predict_one(last_words):
        encoded = numpy.array([[tokenizer.word_index[w] for w in last_words]])
        # predict a word in the vocabulary
        yhat = model.predict_classes(encoded, verbose=0)[0]
        # map predicted word index to word
        next_word = tokenizer.index_word[yhat]
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
