import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import (
    TF2_WEIGHTS_NAME,
    BertConfig,
    BertTokenizer,
    TFBertForTokenClassification)
import tensorflow as tf
from keras.preprocessing.sequence import pad_sequences
from tqdm import tqdm
from seqeval.metrics import classification_report, f1_score


def main():
    df_data = pd.read_csv("csv_dataset.csv", sep=",", encoding="latin1").fillna(method='ffill')
    print(df_data.shape)

    tag_list = df_data.Tag.unique()

    x_train, x_test = train_test_split(df_data, test_size=0.20, shuffle=False)

    print(x_train.shape, x_test.shape)

    agg_func = lambda s: [[w, t] for w, t in zip(s["Word"].values.tolist(), s["Tag"].values.tolist())]

    x_train_grouped = x_train.groupby("Sentence #").apply(agg_func)
    x_test_grouped = x_test.groupby("Sentence #").apply(agg_func)
    x_train_sentences = [[s[0] for s in sent] for sent in x_train_grouped.values]
    x_test_sentences = [[s[0] for s in sent] for sent in x_test_grouped.values]
    x_train_tags = [[t[1] for t in tag] for tag in x_train_grouped.values]
    x_test_tags = [[t[1] for t in tag] for tag in x_test_grouped.values]

    print(np.shape(x_train_tags), np.shape(x_test_tags))

    MAX_LENGTH = 25
    BERT_MODEL = "bert-base-multilingual-cased"

    BATCH_SIZE = 32

    pad_token = 0,
    pad_token_segment_id = 0,
    sequence_a_segment_id = 0,

    MODEL_CLASSES = {"bert": (BertConfig, TFBertForTokenClassification, BertTokenizer)}

    label_map = {label: i for i, label in enumerate(tag_list)}

    num_labels = len(tag_list) + 1
    print(num_labels)

    pad_token_label_id = 0

    config_class, model_class, tokenizer_class = MODEL_CLASSES['bert']
    config = config_class.from_pretrained(BERT_MODEL, num_labels=num_labels)
    tokenizer = tokenizer_class.from_pretrained(BERT_MODEL, do_lower_case=False)
    model = model_class.from_pretrained(
        BERT_MODEL,
        from_pt=bool(".bin" in BERT_MODEL),
        config=config)
    model.layers[-1].activation = tf.keras.activations.softmax

    max_seq_length = 10

    def convert_to_input(sentences, tags):
        input_id_list, attention_mask_list, token_type_id_list = [], [], []
        label_id_list = []

        for x, y in tqdm(zip(sentences, tags), total=len(tags)):

            tokens = []
            label_ids = []

            for word, label in zip(x, y):
                word_tokens = tokenizer.tokenize(word)
                tokens.extend(word_tokens)
                # Use the real label id for the first token of the word, and padding ids for the remaining tokens
                label_ids.extend([label_map[label]] + [pad_token_label_id] * (len(word_tokens) - 1))

            special_tokens_count = 2
            if len(tokens) > max_seq_length - special_tokens_count:
                tokens = tokens[: (max_seq_length - special_tokens_count)]
                label_ids = label_ids[: (max_seq_length - special_tokens_count)]

            label_ids = [pad_token_label_id] + label_ids + [pad_token_label_id]
            inputs = tokenizer.encode_plus(tokens, add_special_tokens=True, max_length=max_seq_length)

            input_ids, token_type_ids = inputs["input_ids"], inputs["token_type_ids"]
            attention_masks = [1] * len(input_ids)

            attention_mask_list.append(attention_masks)
            input_id_list.append(input_ids)
            token_type_id_list.append(token_type_ids)

            label_id_list.append(label_ids)

        return input_id_list, token_type_id_list, attention_mask_list, label_id_list

    input_ids_train, token_ids_train, attention_masks_train, label_ids_train = convert_to_input(x_train_sentences,
                                                                                                x_train_tags)
    input_ids_test, token_ids_test, attention_masks_test, label_ids_test = convert_to_input(x_test_sentences,
                                                                                            x_test_tags)

    input_ids_train = pad_sequences(input_ids_train, maxlen=max_seq_length, dtype="long", truncating="post",
                                    padding="post")
    token_ids_train = pad_sequences(token_ids_train, maxlen=max_seq_length, dtype="long", truncating="post",
                                    padding="post")
    attention_masks_train = pad_sequences(attention_masks_train, maxlen=max_seq_length, dtype="long", truncating="post",
                                          padding="post")
    label_ids_train = pad_sequences(label_ids_train, maxlen=max_seq_length, dtype="long", truncating="post",
                                    padding="post")

   # print(np.shape(input_ids_train), np.shape(token_ids_train), np.shape(attention_masks_train),
        #  np.shape(label_ids_train), )

    input_ids_test = pad_sequences(input_ids_test, maxlen=max_seq_length, dtype="long", truncating="post",
                                   padding="post")
    token_ids_test = pad_sequences(token_ids_test, maxlen=max_seq_length, dtype="long", truncating="post",
                                   padding="post")
    attention_masks_test = pad_sequences(attention_masks_test, maxlen=max_seq_length, dtype="long", truncating="post",
                                         padding="post")
    label_ids_test = pad_sequences(label_ids_test, maxlen=max_seq_length, dtype="long", truncating="post",
                                   padding="post")

    #print(np.shape(input_ids_test), np.shape(token_ids_test), np.shape(attention_masks_test),
         # np.shape(label_ids_test), )

    def example_to_features(input_ids, attention_masks, token_type_ids, y):
        return {"input_ids": input_ids,
                "attention_mask": attention_masks,
                "token_type_ids": token_type_ids}, y

    train_ds = tf.data.Dataset.from_tensor_slices(
        (input_ids_train, attention_masks_train, token_ids_train, label_ids_train)).map(example_to_features).shuffle(
        1000).batch(32).repeat(5)


    test_ds = tf.data.Dataset.from_tensor_slices(
        (input_ids_test, attention_masks_test, token_ids_test, label_ids_test)).map(example_to_features).batch(1)

    #for x, y in test_ds.take(10):
        #print(x, y)

    model.summary()
    optimizer = tf.keras.optimizers.Adam()
    loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    metric = tf.keras.metrics.SparseCategoricalAccuracy('accuracy')

    model.compile(optimizer=optimizer, loss=loss, metrics=[metric])


    history = model.fit(train_ds, epochs=1, validation_data=test_ds)


if __name__ == "__main__":
    main()
