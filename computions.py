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

def get_AUC_nominal(column, y_col, descr_table = None):
    '''Returns AUC for nominal predictor. Levels will be
    displayed in order of increasing part of predicted level.
    Nas in column will be ignored, should be processed before '''
    # inputs:
    # column - pandas.Series predictors column
    # y_col - pandas.Series predicted column
    # descr_table - pandas.DataFrame (optional), out of get_describe_nominal
    #               function for predictor. Will be computed automaticaly by default
    # outputs:
    # dictionary which contains result {<y_levels>:<AUC for this levels>}
    if descr_table is None:
        descr_table = get_describe_nominal(column, y_col)
    
    # in case column has only one level need return 0.5
    # for all y levels - predictor are useless
    if descr_table.shape[0] <= 1:
        return {level : 0.5 for level in y_col.unique()}

    result = {}

    for level in y_col.unique():
        temp_binary_column = y_col.apply(lambda x: 0 if x != level else 1)
        level_distr = descr_table[str(level) + "%"].sort_values()
        numbers = column.replace({n:i for i,n in enumerate(level_distr.index)})
        result[level] = roc_auc_score(temp_binary_column, numbers/sum(numbers))

    return result


def get_full_AUC(column, y_col, predictor_type, descr_table = None):
    '''funciton for getting AUC for any predictor type.
    If returns "showing" AUC - if real AUC less then 0.5
    it doesn't seem that predictor bad - it seems that 
    relationship inverse, so in this case showing AUC is 
    (1 - <real AUC>)'''
    # inputs:
    # column - pandas.Series predictors column
    # y_col - pandas.Series predicted column
    # outputs:
    # dict {<level of y_col>: {"AUC":<showing auc>,
    #                          "rel_type" <rel. type -1/1>,
    #                           "GINI": <GINI>}}
    real_aucs =  (get_AUC_numeric(column, y_col) if predictor_type == 'numeric' 
                 else get_AUC_nominal(column, y_col, descr_table))

    def recomputor(key):
        if real_aucs[key] < 0.5: result = {'AUC': 1 - real_aucs[key],'rel_type': -1}
        else: result = {'AUC' : real_aucs[key], 'rel_type':1}
        result['GINI'] = (result["AUC"] - 0.5)*2
        return result


    showing_aucs = {key: recomputor(key) for key in real_aucs}

    return showing_aucs 