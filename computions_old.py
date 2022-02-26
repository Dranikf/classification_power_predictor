from common.common import nomin_distribution
from common.common import nomin_distribution_parts
from sklearn.metrics import roc_auc_score
from scipy.stats import pearsonr
from scipy.stats import chisquare
import numpy as np
import pandas as pd

def get_describe_numeric(column):
    '''Формирование описательных статистик для численного предиктора'''
    result = pd.DataFrame({"Значение:":column.describe()})
    result['Доля %:'] = np.NaN
    return pd.concat([result, pd.DataFrame({"Значение:":sum(column.isna()), "Доля %:":sum(column.isna())*100/column.shape[0]}, index = ["Emptys"])])


def get_discribe_nominal(column, y_col):
    '''Формирование распределения номинативной переменной + 
    распределение дефолтников'''
    # inputs:
    # columns - pandas.Series содержащий колонку
    # y_col - столбец отклик
    # output - pandas.DataFrame({"Число", "Доля%", "Число дефолтов", "Доля дефолтов%"})
    full_tab = nomin_distribution_parts(column)
    def_tab = nomin_distribution_parts(column[y_col], 
                                       col_name = 'Число дефолтов', 
                                       part_name = 'Доля этой категории в дефолтах%')
    

    result = pd.concat([full_tab, def_tab], axis = 1)
    result['Доля дефолтов в этой категории%'] = result['Число дефолтов']*100 / result['Число']
    
    return result.fillna(0)


def get_AUC_numeric(column, y_col):
    '''функция для получения AUC для численной переменной'''
    # inputs:
    # column - 
    # если вариация переменной нулевая, то нужно записать в auc 0
    if column.var() == 0:
        return 0
    
    return roc_auc_score(y_col, column/sum(column))

def get_AUC_nominal(column, y_col, def_table = None):
    '''Функция вернет AUC для номинальной переменной, 
    предполагается упорядочить уровни переменной по возрастанию
    дефолтности - тогда AUC будет единственным (более того можно доказать
    что это будет максимальный AUC)'''
    # inputs:
    # column - колонка для которой следует провести анализ
    # y_col - столбец отклика
    # disc_table - таблица долей дефолтов для каждого уровня (не обязательный аргумент,
    #              при указании ожидается большая производительность)
    
    # возня с получением def_table
    if def_table is None:
        def_table = nomin_distribution(column[y_col.astype(np.bool8)])/nomin_distribution(column)
        def_table.fillna(0, inplace = True)
    else:
        def_table = def_table.copy()
    
    # перекодировка уровней по возрастанию дефолтности 
    def_table = def_table.sort_values(list(def_table.columns))
    
    # если у def_table всего одна строка то это значит, что переменная вырожденная 
    # и ничего не может дискриминировать, потому надо вернуть 0.5
    if def_table.shape[0] <= 1:
        return 0.5
    
    numbers = column.replace({n:i for i,n in enumerate(def_table.index)})
    return roc_auc_score(y_col, numbers/sum(numbers))

def get_levels_chisq_stat(factor_distr, def_distr):
    '''Тест Хи-квадрат для проверки значимости различий встречаемости
    дефолтов по уроням номинативной переменной'''
    # inputs:
    # factor_distr - распределение всех налюдений по уровням
    # def_distr - распределение дефолтных налюдений по уровням
    # outputs:
    # https://docs.scipy.org/doc/scipy-1.8.0/html-scipyorg/reference/generated/scipy.stats.chisquare.html
    exp_def = factor_distr * (def_distr.sum()/factor_distr.sum())
    return chisquare(def_distr, exp_def)

def get_showing_auc(real_auc):
    '''функция формирует показательный AUC'''
    # inputs:
    # real_auc - реальный AUC
    # outputs:
    # showing_auc - показательный auc
    # rel_check - принимает значение 1 если AUC не был обращен
    
    if real_auc < 0.5:
        showing_auc = 1-real_auc
        rel_check = -1
    else:
        showing_auc = real_auc
        rel_check = 1
        
    return [showing_auc, rel_check]


def get_count_stats(column,y_col):
    '''Полчение "подсчетных" статистик для переданного столбца'''
    
    result = {}
    
    result['Доля пропусков%'] = sum(column.isna())*100/column.shape[0]
    result['Наблюдения доступные для использования'] = sum(np.invert(column.isna()))
    result['Доля дефолтников с пропусками%'] = sum(column[y_col].isna())*100/sum(y_col)
    result['Дефолтники доступные для использования'] = sum(np.invert(column[y_col].isna()))
    
    return result

def computions_fun(column, y_col, is_numeric):
    '''функция которая собирает воедино "вычислительный блок"'''
    # inputs:
    # column - pandas.Series который содержит исследуемый столбец
    # y_col - столбец отклика
    # is_numeric - принимает True если рассматрвиаемая переменная чилсовая False в случае номинативной
    # output: {"discribe_table": <таблица с описательными статитсиками>,
    #          "AUC":<показательный AUC для показателя (реальный AUC может быть < 0.5, при обратной взаимосвязи)>,
    #          "GINI": <GINI для показателя>,
    #          "rel_check":<предполагаемый тип взаимосзази 1 прямая/ -1 обратная (зависит от реального AUC)>
    #          "Chisq": <статистика хи квадрат (только для номинативного)>,
    #          "ChiP": <p-value хи квадрата (только для номинативного)>,
    #          "corr_coef": <коэффициент корреляции Пирсона >,
    #          "corrP: <p-значение для коэффициента коррляции присона> (нолько для численного)",
    #          "empty_part": - <доля пропусков  %>,
    #          "obs_for_using": - <доступно наблюдений>}
    
    count_stats = get_count_stats(column, y_col)
    
    column = column.copy()
    
    if is_numeric:

        
        # создание таблицы с описательными статистиками
        discribe_table = get_describe_numeric(column)
        
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # узкое место! пропуски заменяю медианой
        # это нужно именно перед AUC,corr и chi
        # чтобы таблица была рассчитана с учетом пропусков
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        column[column.isna()] = column.median()
        
        # вычисление реального AUC
        auc = get_AUC_numeric(column, y_col)
        # статитсика хи-квадрат и p-value
        chi_info = [np.NaN, np.NaN]
        # коэффициент корреляции пирсона и p-value
        corr_info = pearsonr(column, y_col)
    else:
        # узкое место! пропуск делаю "дополнительным" уровнем
        column[column.isna()] = "empty"
        
        # все теже дейстивия для номинативной переменной
        discribe_table = get_discribe_nominal(column, y_col)
        auc = get_AUC_nominal(column, y_col, discribe_table.iloc[:,[2]].divide(discribe_table.iloc[:,0],axis='index'))
        chi_info = get_levels_chisq_stat(discribe_table.iloc[:, 0], discribe_table.iloc[:, 2])
        corr_info = [np.NaN, np.NaN]
    
    # формируем показательный AUC
    # если реальный AUC сильно меньше 0,5 это хорошо, просто тип взаимосвязи обратный
    # для удопбства сортровки я ввожу так называемый "показательный" AUC он всегда больше 0.5
    # т.е. если <реальный AUC> < 0.5 => <показательный AUC> = 1 - <реальный AUC>
    # кроме того для того, чтобы понимать обратная взаимосязь или прямая 
    # я введу переменную rel_check (см. описание выше)
    [showing_auc, rel_check] = get_showing_auc(auc)
    
    
    GINI = (auc - 0.5)*2
    result = {'discribe_table':discribe_table, 
              'AUC':showing_auc, 'rel_check': rel_check, 
              'GINI': GINI,'corr_coef':corr_info[0],
              'corrP':corr_info[1], 'Chisq':chi_info[0],
              'ChiP':chi_info[1]}
    
    result = result | count_stats
    
    return result