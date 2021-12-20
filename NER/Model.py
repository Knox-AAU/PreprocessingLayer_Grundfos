import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Model
from keras.layers import merge
from tensorflow.keras import Input
from tensorflow.keras.layers import (
    LSTM,
    Embedding,
    Dense,
    TimeDistributed,
    Dropout,
    Bidirectional,
    Lambda,
    add,
)
from seqeval.metrics import (
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)
import os
import NER2 as ner

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


def runME(dic: dict):
    plt.style.use("ggplot")
    data = pd.read_csv("csv_dataset.csv", encoding="latin1")
    data = data.fillna(method="ffill")
    data.tail(12)
    words = set(list(data["Word"].values))
    words.add("PADword")
    n_words = len(words)
    tags = list(set(data["Tag"].values))
    n_tags = len(tags)

    class SentenceGetter(object):
        def __init__(self, data):
            self.n_sent = 1
            self.data = data
            self.empty = False
            agg_func = lambda s: [
                (w, t)
                for w, t in zip(s["Word"].values.tolist(), s["Tag"].values.tolist())
            ]
            self.grouped = self.data.groupby("Sentence #").apply(agg_func)
            self.sentences = [s for s in self.grouped]

        def get_next(self):
            try:
                s = self.grouped["Sentence: {}".format(self.n_sent)]
                self.n_sent += 1
                return s
            except:
                return None

    getter = SentenceGetter(data)
    sent = getter.get_next()
    print(sent)

    sentences = getter.sentences
    print(len(sentences))

    largest_sen = max(len(sen) for sen in sentences)
    print("biggest sentence has {} words".format(largest_sen))

    max_len = largest_sen
    X = [[w[0] for w in s] for s in sentences]
    new_X = []
    for seq in X:
        new_seq = []
        for i in range(max_len):
            try:
                new_seq.append(seq[i])
            except:
                new_seq.append("PADword")
        new_X.append(new_seq)

    tags2index = {t: i for i, t in enumerate(tags)}
    y = [[tags2index[w[1]] for w in s] for s in sentences]
    y = pad_sequences(
        maxlen=max_len, sequences=y, padding="post", value=tags2index["O"]
    )

    X_tr, X_te, y_tr, y_te = train_test_split(
        new_X, y, test_size=0.1, random_state=2018
    )
    sess = tf.compat.v1.Session()
    tf.compat.v1.keras.backend.set_session(sess)
    tf.compat.v1.disable_eager_execution()
    elmo_model = hub.Module("https://tfhub.dev/google/elmo/2", trainable=True)
    sess.run(tf.compat.v1.global_variables_initializer())
    sess.run(tf.compat.v1.tables_initializer())

    batch_size = 32

    def ElmoEmbedding(x):
        return elmo_model(
            inputs={
                "tokens": tf.squeeze(tf.cast(x, tf.string)),
                "sequence_len": tf.constant(batch_size * [max_len]),
            },
            signature="tokens",
            as_dict=True,
        )["elmo"]

    input_text = Input(shape=(max_len,), dtype=tf.string)
    embedding = Lambda(ElmoEmbedding, output_shape=(max_len, 1024))(input_text)
    x = Bidirectional(
        LSTM(units=256, return_sequences=True, recurrent_dropout=0.2, dropout=0.2)
    )(embedding)
    x_rnn = Bidirectional(
        LSTM(units=256, return_sequences=True, recurrent_dropout=0.2, dropout=0.2)
    )(x)
    x = merge.add([x, x_rnn])  # residual connection to the first biLSTM
    out = TimeDistributed(Dense(n_tags, activation="softmax"))(x)
    model = Model(input_text, out)
    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )

    X_tr, X_val = X_tr[: 73 * batch_size], X_tr[-40 * batch_size :]
    y_tr, y_val = y_tr[: 73 * batch_size], y_tr[-40 * batch_size :]
    y_tr = y_tr.reshape(y_tr.shape[0], y_tr.shape[1], 1)
    y_val = y_val.reshape(y_val.shape[0], y_val.shape[1], 1)
    history = model.fit(
        np.array(X_tr),
        y_tr,
        validation_data=(np.array(X_val), y_val),
        batch_size=batch_size,
        epochs=3,
        verbose=1,
    )

    X_te = X_te[: 9 * batch_size]
    # test_pred = model.predict(np.array(X_te), batch_size=batch_size, verbose=1)
    idx2tag = {i: w for w, i in tags2index.items()}

    def pred2label(pred):
        out = []
        for pred_i in pred:
            out_i = []
            for p in pred_i:
                p_i = np.argmax(p)
                out_i.append(idx2tag[p_i].replace("PADword", "O"))
            out.append(out_i)
        return out

    def test2label(pred):
        out = []
        for pred_i in pred:
            out_i = []
            for p in pred_i:
                out_i.append(idx2tag[p].replace("PADword", "O"))
            out.append(out_i)
        return out

    def prep_pred_labels(predicted_x: list):
        for x in predicted_x:
            for i in range(len(x)):
                if dic.get(x[i]) is not None:
                    x[i] = str(f"B-{dic.get(x[i])}")
                else:
                    x[i] = "O"
        return predicted_x

    x_tee = prep_pred_labels(X_te)
    # pred_labels = pred2label(test_pred)
    test_labels = test2label(y_te[: len(x_tee)])
    print(classification_report(test_labels, x_tee))
    i = 8
    p = model.predict(np.array(X_te[i : i + batch_size]))[0]
    p = np.argmax(p, axis=-1)
    print("{:15} {:5}: ({})".format("Word", "Pred", "True"))
    print("=" * 30)
    for w, true, pred in zip(X_te[i], y_te[i], p):
        if w != "__PAD__":
            print("{:15}:{:5} ({})".format(w, tags[pred], tags[true]))


if __name__ == "__main__":
    print("NER 2")
    csv_data = ner.import_csv()
    dictionary = ner.create_dict(csv_data)
    captions = ner.importJSON()
    tuples = ner.create_tuples(captions, dictionary)
    # print(tuples)
    ner.create_csv_dataset(tuples)
    runME(dictionary)
