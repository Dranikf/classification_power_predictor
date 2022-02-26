# fucnitons for special computions
import pandas as pd
import numpy as np

from sklearn.metrics import roc_auc_score

def get_describe_numeric(column):
    '''Desctibe table for numeric predictor'''
    # inputs:
    # column - pd.Series with column to describe

    result = pd.DataFrame({"Value:":column.describe()})
    result['Part %:'] = np.NaN
    emp_tab = pd.DataFrame({"Value:":sum(column.isna()), 
                            "Part %:":sum(column.isna())*100/column.shape[0]}, 
                            index = ["Emptys"])

        
    return pd.concat([result, emp_tab])


def get_describe_nominal(column, y_col):
    '''disctibution of levels of nominal predictor'''
    # inputs:
    # column - pandas.Series which contains predictor values
    # y_col - pandas.Series which contains predicted value
    # outputs:
    # pandas.DataFrame table wich describes distribution of predictor

    result = pd.DataFrame(column.value_counts())

    for level in y_col.unique():
        
        result[level] = column[y_col == level].value_counts()
        result[str(level) + '%'] = result[level]*100/result.iloc[:,0]
        
    return result.fillna(0)


def get_AUC_numeric(column, y_col):
    '''AUC compution for numeric variable'''
    # inputs:
    # column - pandas.Series predictor column
    # y_col - pandas.Series predicted column
    # outputs:
    # dictionary which contains result {<y_levels>:<AUC for this levels>}
    y_col = y_col[np.invert(column.isna())]
    column = column.dropna()


    result = {}
    

    # for every y_col level we have auc computed as all vs one
    for level in y_col.unique():
        temp_binary_column = y_col.apply(lambda x: 0 if x != level else 1)
        result[level] = (roc_auc_score(temp_binary_column, column/sum(column)) 
                            if column.var() != 0 else 0.5)
        
    return result


#def get_AUC_nominal(column, y_col):

