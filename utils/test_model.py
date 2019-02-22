from sklearn.metrics import accuracy_score, f1_score
from sklearn.base import clone
from sklearn.model_selection import KFold
import keras
from utils.keras_utils import f1_loss
from keras.utils import to_categorical
from keras.preprocessing import sequence
import numpy as np


def single_fold_sklearn(model, X_train, X_test, y_train, y_test, vec):
    X_train = vec.fit_transform(X_train)
    X_test = vec.transform(X_test)
    clf = clone(model)
    clf.fit(X_train, y_train)
    clf.fit(X_train, y_train)
    return clf.predict(X_test)

def single_fold_keras(model, X_train, X_test, y_train, y_test, tokenizer):
    y_train_cat, y_test_cat = to_categorical(y_train), to_categorical(y_test)
    tokenizer.fit_on_texts(X_train)
    list_tokenized_train = tokenizer.texts_to_sequences(X_train)
    list_tokenized_test = tokenizer.texts_to_sequences(X_test)
    X_t = sequence.pad_sequences(list_tokenized_train, maxlen=100)
    X_te = sequence.pad_sequences(list_tokenized_test, maxlen=100)
    
    clf = keras.models.clone_model(model)
    clf.set_weights(model.get_weights())
    clf.compile(loss=f1_loss, optimizer='adam', metrics=['accuracy'])
    clf.fit(X_t, y_train_cat, epochs=5,  batch_size=64,  validation_data=(X_te, y_test_cat))
    
    y_pred_proba = clf.predict(X_te)
    return np.argmax(y_pred_proba, axis=1)

def test_single_model(model, X, y, vec, n_splits=3, random_state=1):
    """
    :param either a Keras Sequential model, or an Sklearn classifier:
    :param either a Keras Tokenizer, or an Sklearn Vectorize:
    :param n_splits: number of folds
    :return: f1 macro score and accuracy
    """
    kf = KFold(n_splits=n_splits, random_state=random_state, shuffle=True)
    f1 = 0
    acc = 0   
    for train_index, test_index in kf.split(X):        
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        if type(model)==keras.engine.sequential.Sequential:
            y_pred = single_fold_keras(model, X_train, X_test, y_train, y_test, vec)
        elif str(type(model)).contains('sklearn'):
            y_pred = single_fold_sklearn(model, X_train, X_test, y_train, y_test, vec)
        else:
            print("Model not supported")
        f1 += f1_score(y_pred, y_test, average="macro")
        acc += accuracy_score(y_pred, y_test)       
    return f1/n_splits, acc/n_splits