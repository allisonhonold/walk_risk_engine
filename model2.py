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

def stamp_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)


def print_scores(true, pred, pred_proba):
    lloss = log_loss(true, pred_proba)
    cf = confusion_matrix(true, pred)
    acc = accuracy_score(true, pred)
    f1 = f1_score(true, pred)
    print(f"log loss: {lloss}\n\nconfusion matrix:\n{cf}\naccuracy: {acc}\n"
        + f"F1 score: {f1}")

    
def categorize_arrests(dataframe):
    cat_df = dataframe.copy()
    cat_df.loc[cat_df['n_arrests'] > 0] = 1
    cat_df['n_arrests'] = cat_df['n_arrests'].fillna(value=0)
    return cat_df


def split_last(dataframe, sort_col='date', cut=.9):
    if sort_col != None:
        dataframe = dataframe.sort_values(by=sort_col, axis='columns')
    cutoff = dataframe.shape[0]*cut
    first_df = dataframe.reset_index(drop=True).loc[:cutoff]
    last_df = dataframe.reset_index(drop=True).loc[cutoff:]
    X_train = first_df.drop(columns=['n_arrests'])
    y_train = first_df['n_arrests']
    X_eval = last_df.drop(columns=['n_arrests'])
    y_eval = last_df['n_arrests']
    return X_train, y_train, X_eval, y_eval


def log_loss_cvs(pipe, X_train, y_train):
    ll_scorer = make_scorer(log_loss, greater_is_better=True, needs_proba=True)

    stamp_time()
    scores = cross_val_score(pipe, X_train, y_train, scoring=ll_scorer, cv=5)
    stamp_time()
    print(scores)
    print(
        f"95% CI Accuracy: "
        f"{round(scores.mean(), 2)} "
        f"(+/- {round(scores.std() * 2, 2)})"
    )


def main():
    # df = pd.read_sql_table('manhattan_loc_d_ar_wea', 'postgresql:///walk')
    df = pd.read_sql_query("""
                        SELECT latitude, 
                                longitude, 
                                ap_t_high100, 
                                n_arrests
                        FROM manhattan_loc_d_ar_wea 
                        ;"""
                        , 'postgresql:///walk')
    categorized_df = categorize_arrests(df)

    # add combined lat/long location feature
    categorized_df['latlong'] = (categorized_df['latitude'].astype(str) 
                                + categorized_df['longitude'].astype(str))
    X_train, y_train, X_eval, y_eval = split_last(categorized_df, sort_col=None)

    column_transformer = ColumnTransformer( 
        transformers=[
        ('ohe', OneHotEncoder(categories='auto'), ['latlong']),
        ('ss', StandardScaler(), ['latitude', 'longitude', 'ap_t_high100'])],
        remainder='drop')

    rfc = RandomForestClassifier(n_estimators=10, random_state=5, max_depth=10,
                            class_weight='balanced')

    pipe = Pipeline([
        ('preprocessor', column_transformer),
        ('model', rfc)
    ])

    stamp_time()
    train_probas = pipe.fit_predict(X_train, y_train)
    print(f"training neg log loss: {log_loss(y_train, train_probas)}")
    test_probas = pipe.predict(X_eval)
    print(f"test neg log loss: {log_loss(y_eval, test_probas)}")
    stamp_time()



if __name__ == __name__:
    main()