import numpy as np
import pandas as pd

from gensim import corpora
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from nltk.stem import SnowballStemmer

from keras.preprocessing import sequence
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Embedding
from keras.layers import LSTM, GRU, SimpleRNN
from sklearn import preprocessing
from sklearn.metrics import (precision_score, recall_score,
                             f1_score, accuracy_score,mean_squared_error,mean_absolute_error)
np.random.seed(0)
from keras import callbacks
from keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, CSVLogger

if __name__ == "__main__":

    train_df = pd.read_csv('data/training_tweets_ca.txt', sep='\t',header=0)
    classlabels = pd.read_csv('data/training_truth_ca.txt', header=0)

    raw_docs_train = train_df['phrase'].values
    classlabels1 = classlabels['label'].values
    print(classlabels1.shape)
    print(len(raw_docs_train))
    print(raw_docs_train[4318])
                
    stop_words = set(stopwords.words('dutch'))
    stop_words.update(['.', ',', '"', "'", ':', ';', '(', ')', '[', ']', '{', '}'])
    stemmer = SnowballStemmer('dutch')

    print "pre-processing train docs..."
    processed_docs_train = []
    for doc in raw_docs_train:
       doc = doc.decode("utf8")
       tokens = word_tokenize(doc)
       filtered = [word for word in tokens if word not in stop_words]
       stemmed = [stemmer.stem(word) for word in filtered]
       processed_docs_train.append(stemmed)
   
    processed_docs_all = processed_docs_train

    dictionary = corpora.Dictionary(processed_docs_all)
    dictionary_size = len(dictionary.keys())
    print "dictionary size: ", dictionary_size 
    
    print "converting to token ids..."
    word_id_train, word_id_len = [], []
    for doc in processed_docs_train:
        word_ids = [dictionary.token2id[word] for word in doc]
        word_id_train.append(word_ids)
        word_id_len.append(len(word_ids))

    seq_len = np.round((np.mean(word_id_len) + 2*np.std(word_id_len))).astype(int)

    #pad sequences
    word_id_train = sequence.pad_sequences(np.array(word_id_train), maxlen=seq_len)
       
    num_labels = 3
    print(classlabels1)
    y_train_enc = np_utils.to_categorical(classlabels1)

    #LSTM
    print "fitting LSTM ..."
    model = Sequential()
    model.add(Embedding(dictionary_size, 256, dropout=0.2))
    model.add(SimpleRNN(256, dropout_W=0.2, dropout_U=0.2))
    model.add(Dense(num_labels))
    model.add(Activation('softmax'))
    
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    checkpointer = callbacks.ModelCheckpoint(filepath="logs1/checkpoint-{epoch:02d}.hdf5", verbose=1, save_best_only=True, monitor='loss')
    csv_logger = CSVLogger('logs1/training_set_iranalysis1.csv',separator=',', append=False)

    model.fit(word_id_train, y_train_enc, nb_epoch=1000, batch_size=32, validation_split=(0.33), verbose=1, callbacks=[checkpointer,csv_logger])
    model.save("logs1/lstm_model.hdf5")
    

