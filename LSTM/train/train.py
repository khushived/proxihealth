import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import warnings
warnings.filterwarnings('ignore',category=FutureWarning)

import numpy as np
import pandas as pd
import pickle as pkl
import tensorflow.keras.backend as K

from tensorflow.keras.models import Sequential

from tensorflow.keras import regularizers
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Embedding
from tensorflow.keras.layers import BatchNormalization

EPOCHS = 15
MAX_LEN = 100
LSTM_DIM = 100
DENSE_DIM = 50
BATCH_SIZE = 16
VECTOR_DIM = 50

def getData():
    tweets = np.load('../data/processed/tokenized_tweets.npy')
    category = pd.read_csv('../../Scraper/data/data_annotated.csv')['y'].values.reshape(-1,1)
    return tweets, category

def getDict():
    numToVector = pkl.load(open('../data/processed/num_to_vec.pkl','rb'))
    return numToVector

def getEmbedMatrix(numToVector):

    embed_matrix = np.zeros((len(numToVector), VECTOR_DIM))

    for i in range(len(numToVector)):

        embed_matrix[i] = numToVector[i]

    return embed_matrix

def getModel(embed_matrix): 

    model = Sequential()
    model.add(Input(shape=(MAX_LEN,)))
    model.add(Embedding(len(embed_matrix),
                        output_dim = VECTOR_DIM,
                        input_length = MAX_LEN,
                        mask_zero = True,
                        trainable = False))
    model.add(BatchNormalization())
    model.add(Dropout(0.2))
    model.add(LSTM(LSTM_DIM, recurrent_dropout=0.2))
    model.add(BatchNormalization())
    model.add(Dropout(0.2))
    model.add(Dense(DENSE_DIM))
    model.add(BatchNormalization())
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    
    return model

def trainModel():

    tweets, category = getData()
    numToVector = getDict()

    embed_matrix = getEmbedMatrix(numToVector)

    model = getModel(embed_matrix)

    print(model.summary())

    x = tweets
    y = category
    
    history = model.fit(x, y, epochs=EPOCHS, batch_size=BATCH_SIZE, shuffle=True)

    model.save('../data/model.h5')

trainModel()