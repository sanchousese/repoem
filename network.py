from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.optimizers import SGD
import numpy as np
import sys
import random

text = open(str(sys.argv[1])).read().lower()
print('corpus length:', len(text))

chars = set(text)
print('total chars:', len(chars))
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))

maxlen = 20
step = 3
sentences = []
next_chars = []
for i in range(0, len(text) - maxlen, step):
    sentences.append(text[i: i + maxlen])
    next_chars.append(text[i + maxlen])
print('nb sequences:', len(sentences))

print('Vectorization...')
X = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
for i, sentence in enumerate(sentences):
    for t, char in enumerate(sentence):
        X[i, t, char_indices[char]] = 1
    y[i, char_indices[next_chars[i]]] = 1

print('Build model...')
model = Sequential()
model.add(LSTM(len(chars), 512, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(512, 512, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(512, len(chars)))
model.add(Activation('softmax'))
sgd = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd)


def sample(a, temperature=1.0):
    a = np.log(a) / temperature
    a = np.exp(a) / np.sum(np.exp(a))
    return np.argmax(np.random.multinomial(1, a, 1))

# make 1..60
for iteration in range(1, 2):
    model.fit(X, y, batch_size=128, nb_epoch=1)
    model.save_weights(str(sys.argv[1]) + "-model", overwrite=True)

start_index = random.randint(0, len(text) - maxlen - 1)

resultString = ''
for diversity in [0.8, 1.1]:
    # print()
    # print('----- diversity:', diversity)
    resultString += '----- diversity:' + str(diversity) + '\n'
    generated = ''
    sentence = text[start_index: start_index + maxlen]
    generated += sentence
    # print('----- Generating with seed: "' + sentence + '"')
    # sys.stdout.write(generated)

    for iteration in range(400):
        x = np.zeros((1, maxlen, len(chars)))
        for t, char in enumerate(sentence):
            x[0, t, char_indices[char]] = 1.

        preds = model.predict(x, verbose=0)[0]
        next_index = sample(preds, diversity)
        next_char = indices_char[next_index]

        generated += next_char
        sentence = sentence[1:] + next_char
        # sys.stdout.write(next_char)
        # sys.stdout.flush()
        resultString += sentence + "\n"
    print()

f = open(str(sys.argv[1]) + '-result', 'w+')
f.write(resultString)
f.close()
