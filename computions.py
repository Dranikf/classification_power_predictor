# fucnitons for special computions
import pandas as pd
import numpy as np
from scipy.stats import kstwo

from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
from sklearn.metrics import auc



#==========================Real computions========================================
def get_describe_numeric(column):
    '''Desctibe table for numeric predictor'''
    # inputs:
    # column - pd.Series with column to describe

    result = pd.DataFrame({"Value:":column.describe()})
    result['Part %:'] = np.NaN
    emp_tab = pd.DataFrame({
        "Value:":sum(column.isna()), 
        "Part %:":sum(column.isna())*100/column.shape[0]
    }, index = ["Empty"])

        
    return pd.concat([result, emp_tab])


def get_describe_nominal(column, y_col):
    '''Disctibution of levels of nominal predictor'''
    # inputs:
    # column - pandas.Series which contains predictor values
    #          na values should be replaced
    # y_col - pandas.Series which contains predicted value
    # outputs:
    # pandas.DataFrame table wich describes distribution of predictor

    result = pd.DataFrame(column.value_counts())

    for level in y_col.unique():
        
        result[level] = column[y_col == level].value_counts()
        result[str(level) + '%'] = result[level]*100/result.iloc[:,0]
        
    result.rename(columns = {column.name : 'count'}, inplace = True)
    result.index.names = [column.name]
    return result.fillna(0)


def get_KS_ts_pvalue(y_col, level, KS_stat):
    '''Get two side p-value for KS stat'''
    # inputs:
    # y_col - column with discriminant values
    # level - value of y_col which will be regarded as True
    # KS_stat - statistic for which is calculated p-value
    # outputs:
    # p-value
    n = sum(y_col == level)
    m = sum(y_col != level)
    en = n*m/(n+m)
    
    return kstwo.sf(KS_stat, np.round(en))

def get_all_stats_for_given_predictor(column, y_col, level):
    '''The service function for stats compution
    at the stage when all values are reduced to numeric form'''
    result = {}

    temp_binary_column = y_col.apply(lambda x: 0 if x != level else 1)
    col_norm = (column - np.min(column))/(np.max(column) - np.min(column))
    fpr, tpr, _ = roc_curve(temp_binary_column, col_norm)
    result['AUC'] = (auc(fpr, tpr) if column.var() != 0 else 0.5)
    result['KS'] = np.max(np.abs(fpr - tpr))
    result['KS_p_val'] = get_KS_ts_pvalue(y_col, level, result['KS'])
    
    return result 
    

def get_stats_numeric(column, y_col):
    '''Statistics of categorizing ability for column'''
    # inputs:
    # column - pandas.Series predictor column
    # y_col - pandas.Series predicted column
    # outputs:
    # dictionary which contains result {<y_levels>:{
        #"AUC":<AUC for this levels>,
        #"KS": <KS for this levels>,
        #"KS_p_vlaue" : <p-value for two sied KS test>
    #}}
    #print('this funciton should replace get_AUC_numeric')
    y_col = y_col[np.invert(column.isna())]
    column = column.dropna()

    result = {}

    # for every y_col level we have auc, KS, and pvalue computed as all vs one
    for level in y_col.unique():
        result[level] = get_all_stats_for_given_predictor(column, y_col, level)
        
    return result


def get_stats_nominal(column, y_col, descr_table = None):
    '''Returns AUC for nominal predictor. Levels will be
    displayed in order of increasing part of predicted level.
    Nas in column will be ignored, should be processed before '''
    # inputs:
    # column - pandas.Series predictors column
    # y_col - pandas.Series predicted column
    # descr_table - pandas.DataFrame (optional), out of get_describe_nominal
    #               function for predictor. Will be computed automaticaly by default
    # outputs:
    # dictionary which contains result {<y_levels>:{
        #"AUC":<AUC for this levels>,
        #"KS": <KS for this levels>,
        #"KS_p_vlaue" : <p-value for two sied KS test>
    #}}
    if descr_table is None:
        descr_table = get_describe_nominal(column, y_col)
    
    # in case column has only one level need return 0.5
    # for all y levels - predictor are useless
    if descr_table.shape[0] <= 1:
        return {level : 0.5 for level in y_col.unique()}

    result = {}

    for level in y_col.unique():
        level_distr = descr_table[str(level) + "%"].sort_values()
        numbers = column.replace({n:i for i,n in enumerate(level_distr.index)})
        
        result[level] = get_all_stats_for_given_predictor(numbers, y_col, level)

    return result


def get_full_stats(column, y_col, predictor_type, descr_table = None):
    '''Funciton for getting AUC and other statistics
    for any predictor type. If returns "showing" AUC - 
    if real AUC less then 0.5 it doesn't seem that 
    predictor bad - it seems that relationship inverse, 
    so in this case showing AUC is (1 - <real AUC>). 
    All inputs must be without nas!'''
    # inputs:
    # column - pandas.Series predictors column
    # y_col - pandas.Series predicted column
    #                   
    # outputs:
    # dict {<level of y_col>: {"AUC":<showing auc>,
    #                          "KS": KS statistics
    #                          "KS_p_value": p value for two side KS test
    #                          "rel_type" <rel. type -1/1>,
    #                           "GINI": <GINI>}}

    if predictor_type == 'numeric':
        stats = get_stats_numeric(column, y_col)
    else:
        stats = get_stats_nominal(column, y_col, descr_table)
    
    
    for y_level in stats:
        stats[y_level]["AUC"], stats[y_level]['rel_type'] = \
            [stats[y_level]["AUC"], 1] \
            if stats[y_level]["AUC"] > 0.5\
            else [1 - stats[y_level]["AUC"], -1]
        
        
        y_eq_level_cond = (y_col == y_level)
        y_lev_count = sum(y_eq_level_cond)
        y_emp_count = sum(column.isna())
        
        stats[y_level]["GINI"] = (stats[y_level]["AUC"] - 0.5)*2
        stats[y_level]["Count"] = y_lev_count
        stats[y_level]["Empty"] = sum(column[y_eq_level_cond].isna())
        stats[y_level]["Empty% in level"] = (stats[y_level]["Empty"]*100)/y_lev_count
        stats[y_level]["Empty% in all Empty"] = \
            (stats[y_level]["Empty"]*100)/y_emp_count\
            if y_emp_count != 0 else 0.0

    return stats

def get_all_comuptions(column, y_col, fillna_nominal = 'Empty'):
    '''Realise all computions for each column'''
    # inputs:
    # column - pandas.Series predictors column
    # y_col - pandas.Series predicted column
    # fillna_nominal -  optional, the value vich will replace na-values
    #                   "Empty" by default

    new_column_data = {}
    new_column_data['name'] = column.name
    new_column_data['empty count'] = sum(column.isna())
    new_column_data['empty part'] = (new_column_data['empty count'] / 
                                      column.shape[0])


    is_numeric = np.isin(column.dtype, 
                        [np.int64, np.float64, np.int32, np.float64])

    if is_numeric:
        new_column_data['predictor_type'] = 'numeric'
        new_column_data['describe_table'] = get_describe_numeric(column)
                
    else:
        new_column_data['predictor_type'] = 'nominal'
        column = column.fillna(fillna_nominal)
        new_column_data['describe_table'] = get_describe_nominal(column, y_col)

    new_column_data['stats_result'] = get_full_stats( 
        column, y_col, new_column_data['predictor_type'],
        descr_table = new_column_data['describe_table']
    )
            
    return new_column_data

#==========================Real computions========================================

#==========================Data represintations===================================

def stats_info_to_DataFrame(stats_info, predictors_name = None):
    '''Recording structure of dicts describing AUC and same 
    inicators into multiindex column dataframe'''
    # stats_info - get_full_computions function output
    # predictors_name - name of predictor, will be used as
    #                   index for new columns
    headers_tuples = []
    line_numbers = []

    # preparing new line and multiindex
    for level in stats_info:
        for indicator in stats_info[level]:
            headers_tuples.append((level, indicator))
            line_numbers.append(stats_info[level][indicator])

    col_ind = "0" if predictors_name is None else predictors_name

    # creating DataFrame
    result = pd.DataFrame(columns = pd.MultiIndex.from_tuples(headers_tuples))
    result.loc[col_ind, :] = line_numbers
    return result

def get_predictor_row(column_data):

    result = stats_info_to_DataFrame(column_data['stats_result'], column_data['name'])
    result['Empty'] = column_data['empty count']
    result['Empty part'] = column_data['empty part']
    return result

#==========================Data represintations===================================    