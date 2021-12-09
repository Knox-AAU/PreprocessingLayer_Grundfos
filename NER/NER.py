from keras.preprocessing.sequence import pad_sequences
import extract_JSON

from sklearn.model_selection import train_test_split
import tensorflow as tf
import tensorflow_hub as hub
from keras import backend as K

def vectorization(data : dict):

    max_len = 2

    tags2index = {t:i for i,t in enumerate()}
    y = [[tags2index[w[1]] for w in s] for s in data]
    y = pad_sequences(maxlen=max_len, sequences=y, padding="post", value=tags2index["O"])
    y[15]

    return data


def leTrain():

    data = vectorization()

    X_tr, X_te, y_tr, y_te = train_test_split(data, y, test_size=0.1, random_state=2018)
    sess = tf.Session()
    K.set_session(sess)
    elmo_model = hub.Module("https://tfhub.dev/google/elmo/2", trainable=True)
    sess.run(tf.global_variables_initializer())
    sess.run(tf.tables_initializer())