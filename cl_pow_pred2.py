import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

def pred_auc(y, X):
    '''
        Compute AUC for classification model based on
        one numeric predictor.
        Input:
            y - 1-D binary array;
            X - 1-D float array.
        Output:
            float AUC.
    '''
    norm_X = (X - np.min(X))/ (np.max(X) - np.min(X))
    return roc_auc_score(y, X)

def cut_as_scores(y, X):
    '''
        Recode categorial variable as scores 
        of classification model, where estimation of probability of y == 1,
        for category `a` is `count(y == 1 and X == `a`)/count(X = `a`)`
        Inputs:
            y - 1-D binary np.array, classes of observations;
            X - 1-D np.array, category variable wich nee to be recoded.
        Output:
            1-D np.array
    '''
    
    test_tab = pd.crosstab(X, y)
    cut_p_hat = (test_tab.iloc[:, 1]/test_tab.sum(axis = 1))
    return np.fromiter(map(lambda val: cut_p_hat[val], X), np.float32)


def cat_auc(y, X):
    '''
        Compute AUC for classification model based on
        one categpial predictor. For model details look 
        for `cut_as_scores` function.
        Inputs:
            y - 1-D binary np.array, classes of observations;
            X - 1-D np.array, category variable wich nee to be recoded.
        Output:
            float AUC.
    '''
    
    return roc_auc_score(y, cut_as_scores(y, X))
    
    