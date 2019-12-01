# import necessary packages
from datetime import datetime
from sklearn.metrics import (log_loss, confusion_matrix, accuracy_score, 
                            f1_score, make_scorer)
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import joblib


def stamp_time():
    """stamps the time in the terminal.
    """
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)


def print_scores(true, pred, pred_proba):
    """prints the log loss, confusion matrix, accuracy, and F1 score

    Args:
        true: true values
        pred: predicted values
        pred_proba: predicted probabilities
    """
    lloss = log_loss(true, pred_proba)
    cf = confusion_matrix(true, pred)
    acc = accuracy_score(true, pred)
    f1 = f1_score(true, pred)
    print(f"log loss: {lloss}\n\nconfusion matrix:\n{cf}\naccuracy: {acc}\n"
        + f"F1 score: {f1}")

    
def categorize_arrests(dataframe):
    """categorizes arrests into boolean 1 if 1+ arrests, 0 if no arrests

    Args:
        dataframe: a pandas dataframe with column 'n_arrests' to be transformed
    
    Returns:
        cat_df: a copy of the original dataframe with column 'n_arrests' filled
        with 1 and 0 for arrest(s)/no arrests
    """
    cat_df = dataframe.copy()
    cat_df['n_arrests'] = cat_df['n_arrests'].fillna(value=0)
    cat_df['n_arrests'] = cat_df['n_arrests'].astype(int)
    cat_df.loc[cat_df['n_arrests'] > 0, 'n_arrests'] = 1
    return cat_df


def split_last(dataframe, target_col, sort_col='date', cut=.9):
    """Splits the dataframe on sort_column at the given cut ratio, and splits
    the target column

    Args:
        dataframe: dataframe to be cut
        sort_col: column to be sorted on. Default='date'
        cut: cut ratio for the train/eval sets

    Returns:
        X_train: dataframe of the first cut of the data set without the target
        y_train: dataframe  of the first cut of the data set only target values
        X_eval: dataframe of the remaining slice of the data set without target
        y_eval: dataframe of the remaining slice of the data set only targets
    """
    if sort_col != None:
        dataframe = dataframe.sort_values(by=sort_col, axis='columns')
    cutoff = dataframe.shape[0]*cut
    first_df = dataframe.reset_index(drop=True).loc[:cutoff]
    last_df = dataframe.reset_index(drop=True).loc[cutoff:]
    X_train = first_df.drop(columns=[target_col])
    y_train = np.array(first_df[target_col]).ravel()
    X_eval = last_df.drop(columns=[target_col])
    y_eval = np.array(last_df[target_col]).ravel()
    return X_train, y_train, X_eval, y_eval


def log_loss_cvs(pipe, X_train, y_train, cv=5):
    """performs and prints results of cross_val_score with log_loss as scorer

    Args:
        pipe: pipeline or model
        X_train: training set
        y_train: training targets
        cv: cross validation splitting strategy. Default: 5-fold
    """
    ll_scorer = make_scorer(log_loss, greater_is_better=True, needs_proba=True)

    scores = cross_val_score(pipe, X_train, y_train, scoring=ll_scorer, cv=cv)
    print(scores)
    print(
        f"95% CI log loss: "
        f"{round(scores.mean(), 2)} "
        f"(+/- {round(scores.std() * 2, 2)})"
    )


def evaluate_model(pipe, X_train, y_train, X_eval, y_eval):
    """prints model evaluation metrics: training log loss, testing log loss,
    confusion matrix, accuracy, F1

    Args:
        pipe: pipeline or model
        X_train: training set
        y_train: training targets
        X_eval: evaluation/test set
        y_eval: evaluation/test set
    """
    print("fitting model")
    pipe.fit(X_train, y_train)
    print("model fit. Predicting for training set")
    train_probas = pipe.predict_proba(X_train)
    print(f"training log loss: {log_loss(y_train, train_probas)}")
    test_probas = pipe.predict_proba(X_eval)
    test_predict = pipe.predict(X_eval)
    print(f"test neg log loss: {log_loss(y_eval, test_probas)}")
    print(f"confusion matrix: \n{confusion_matrix(y_eval, test_predict)}")
    print(f"accuracy: {accuracy_score(y_eval, test_predict)}")
    print(f"F1: {f1_score(y_eval, test_predict)}")


def joblib_pipeline(pipeline, file_name="pipeline.joblib"):
    """pickles/joblibs the pipeline to the specified file_name

    Args:
        pipeline: fit pipeline
        file_name: name or path of file to be created. Default: pipeline.joblib
    """
    output_file = open(file_name, "wb")
    joblib.dump(pipeline, output_file)
    output_file.close()


def main():
    pass


if __name__ == "__main__":
    main()