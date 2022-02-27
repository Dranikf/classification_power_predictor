import pandas as pd;
import numpy as np;
from computions import *
from writing import *


class classification_power_predictor():


    _predictors_data = None
    header_creator = default_header_creator
    default_header_format = {'bold': 1, 'border': 1, 'align': 'center', 
                            'valign': 'vcenter', 'fg_color': '#C0C0C0',
                            'font_size':15}

    def __init__(self, table, y_col) -> None:
        # inputs:
        # table - pandas.DataFrame wich contains
        # y_col - pandas.Series model output column(Y)

        self._table = table
        self._y_col = y_col


    # BIG methods======================================================================
    def update_predictors(self, fillna_nominal = None):
        '''refresh computing parameters according with current table'''
        # inputs:
        # fillna_nominal -  optional, the value vich will replace na-values
        #                   for the nominal predictors, in other way, they
        #                   will be ignored  

        self._predictors_data = {}


        for col_name in self._table.columns:
            new_column_data = {}
            new_column_data['name'] = col_name
            new_column_data['emptys_count'] = sum(self._table[col_name].isna())


            is_numeric = np.isin(self._table[col_name].dtype, 
                                [np.int64, np.float64, np.int32, np.float64])

            if is_numeric:
                new_column_data['predictor_type'] = 'numeric'
                new_column_data['describe_table'] = get_describe_numeric(self._table[col_name])
                
            else:
                new_column_data['predictor_type'] = 'nominal'
                new_column_data['describe_table'] = get_describe_nominal(self._table[col_name], self._y_col)
                    

            computions_column = (self._table[col_name].fillna(fillna_nominal)
                                if (not(fillna_nominal is None) and not(is_numeric))
                                else self._table[col_name])
            
            new_column_data['AUC_data'] = get_full_AUC( computions_column,
                                                        self._y_col,
                                                        new_column_data['predictor_type'],
                                                        new_column_data['describe_table'])


            self._predictors_data[col_name] = new_column_data



    def write_to_book(self, xl_writer):
        '''metod creates, sheet for every predictor in table'''
        # xl_writer - pandas.io.excel._xlsxwriter.XlsxWriter wich will be used for book saving

        default_header_format = xl_writer.book.add_format(self.default_header_format)

        for col_data in self._predictors_data.values():
            curr_shit_name = add_sheet(xl_writer, col_data['name'])
            self.header_creator(xl_writer.sheets[curr_shit_name], col_data, default_header_format)
            
    # BIG methods======================================================================


    # getters==========================================================================
    def get_predictors_data(self):
        '''getter for predictors data'''
        return self._predictors_data
    # getters==========================================================================