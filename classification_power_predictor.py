import pandas as pd;
import numpy as np;
from computions import *
from writing import *


class classification_power_predictor():


    _predictors_data = None
    # funcotion wich will be called for every predictor
    # for display infor at list
    predictor_printer = default_predictor_printer
    default_header_format = {'bold': 1, 'border': 1, 'align': 'center', 
                            'valign': 'vcenter', 'fg_color': '#C0C0C0',
                            'font_size':15}
    default_header_printer = default_header_printer
    default_tab_head_pr = print_table_header
    

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
        self.result_DF = pd.DataFrame()

        for col_name in self._table.columns:


            #self.result_DF = pd.concat([self.result_DF, get_predictor_row(new_column_data)], axis = 0) 

            self._predictors_data[col_name] = get_all_comuptions(self._table[col_name], self._y_col)



    def write_to_book(self, xl_writer):
        '''metod creates, sheet for every predictor in table'''
        # xl_writer - pandas.io.excel._xlsxwriter.XlsxWriter wich will be used for book saving
        self.my_writer = xl_writer
        my_formats = {'header_format':xl_writer.book.add_format(self.default_header_format),
                      'desc_format':xl_writer.book.add_format(self.default_header_format)}

        for col_data in self._predictors_data.values():
            curr_shit_name = add_sheet(xl_writer, col_data['name'])
            self.predictor_printer( xl_writer.sheets[curr_shit_name],
                                    col_data, my_formats)
        del self.my_writer

            
    # BIG methods======================================================================





    # getters==========================================================================
    def get_predictors_data(self):
        '''getter for predictors data'''
        return self._predictors_data
    # getters==========================================================================