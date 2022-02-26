import pandas as pd
import numpy as np

def nomin_distribution(column, empty_show = False, col_name = 'Число'):
    '''фнукция для формирования таблицы распределения номинативного предиктора'''
    # inputs:
    # column - входная колонка
    # empty_show - переменная указывает выводить ли в таблице информацию о пропусках
    # output - на выходе таблица ставит в соответсвие уровни переданной колонки и число их встречь  переданной колонке
    # col_name - наименование столбца в котором будут записаны частоты
    
    column = column.copy()
    if empty_show:
        column.loc[column.isna()] = "empty"
    result = pd.DataFrame(column.groupby(column, dropna = False).count())
    result.columns = [col_name]
    return result

def nomin_distribution_parts(column, empty_show = True, abs_show = True, col_name = 'Число', part_name = "Доля %"):
    '''функция для формирования таблицы распределения номинативного предиктора 
    с включением долей'''
    # inputs:
    # column - входная колонка
    # empty_show - переменная указывает выводить ли в таблице информацию о пропусках
    # output - на выходе таблица ставит в соответсвие уровни переданной колонки и число их встречь  переданной колонке
    # abs_show - выводить ли колонку с абсолютными занчениями
    # col_name - наименование столбца в котором будут записаны частоты
    # patr_name - наимнование столбца в котором будут записаны частости
    
    result = nomin_distribution(column, empty_show = empty_show, col_name = col_name)
    result[part_name] = result[col_name]*100/sum(result[col_name])
    
    return result if abs_show else result[[part_name]]


def get_in_pattern_rows(column, sub_strings):
    '''Поиск подстрок в колонке не зависимо от регистра и пробелов'''
    # inputs:
    # column - колонка по которой будет осущетствляться поиск
    # sub_strings - list с подстроками которые требуется отыскать
    # output:
    # boolean iterator который выделит записи в которых найдены искомые подстроки
    
    condition = np.zeros(column.shape[0]).astype('bool')
    
    for sub_str in sub_strings:
        find_str = sub_str.replace(' ', '').lower()
        print(find_str)
        condition = condition | (column.str.replace(' ', '').str.lower().str.find(find_str) != -1)
        
    return condition