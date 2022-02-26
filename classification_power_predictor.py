import pandas as pd;
import numpy as np;
from computions import *


class classification_power_predictor():


    _predictors_data = None

    def __init__(self, table, y_col) -> None:
        # inputs:
        # table - pandas.DataFrame wich contains
        # y_col - pandas.Series model output column(Y)

        self._table = table
        self._y_col = y_col


    # BIG methods======================================================================
    def update_predictors(self, fillna_nominal):
        '''refresh computing parameters according with current table'''
        # inputs: 

        self._predictors_data = []


        for col_name in self._table.columns:
            new_column_data = {}
            new_column_data['name'] = col_name

            is_numeric = np.isin(self._table[col_name].dtype, 
                                [np.int64, np.float64, np.int32, np.float64])
            new_column_data['predictor_type'] = 'numeric' if is_numeric else 'nominal'

            new_column_data['describe_table'] = (get_describe_numeric(self._table[col_name])
                                                    if is_numeric
                                                    else get_describe_nominal(self._table[col_name], self._y_col))
            
            #new_column_data['AUC'], new_column_data['type_of_rel'], 
            #new_column_data['GINI'] =  


            self._predictors_data.append(new_column_data)
            #self._predictors_data['describe_table']



    def write_to_book(self, xl_writer):
        '''metod creates, sheet for every predictor in table'''
        # xl_writer - pandas.io.excel._xlsxwriter.XlsxWriter wich will be used for book saving

        for col_data in self._predictors_data:
            self._add_sheet(xl_writer, col_data['name'])
            
    # BIG methods======================================================================


    # compution methods ===============================================================

    
    def _get_full_AUC(self, column):



        pass
    # compution methods ===============================================================


    # excel writing methods ===========================================================
    def _add_sheet(self, xl_writer, sheet_name):
        '''Adding a sheet with setted name.
        Illegal characters will be removed.
        If name is too long it will be cutted.
        If there is same names they will be numerated.'''
        # inputs:
        # xl_writer - книга на которую надо добавить лист
        # sheet_name - название создаваемого листа
        
        sheet_name = sheet_name.replace('/', ' ')
        sheet_name = sheet_name if len(sheet_name) < 31 else sheet_name[0:31]
        
        # нужно удостовериться что такого-же названия нет
        # если есть то изменим последний символ так, чтобы
        # было правильно
        i = 2
        while sheet_name in xl_writer.sheets.keys():
            temp = list(sheet_name) 
            if len(sheet_name) == 31 or i > 2: temp[-1] = str(i)
            else: temp.append(str(i))

            i += 1
            sheet_name = "".join(temp)
        
        result_sheet = xl_writer.book.add_worksheet(sheet_name)
        xl_writer.sheets[sheet_name] = result_sheet
        
        return sheet_name
    # excel writing methods ===========================================================


    # getters==========================================================================
    def get_predictors_data(self):
        '''getter for predictors data'''
        return self._predictors_data
    # getters==========================================================================