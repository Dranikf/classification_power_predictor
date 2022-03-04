import imp
from xlsxwriter.utility import xl_cell_to_rowcol, xl_rowcol_to_cell
from DS_common.excel_writing import save_double_column_df


def default_header_printer(calling_obj, sheet, predictors_data, format):
    '''Defatul funciton for header creator'''
    # inputs:
    # calling_obj - object that called the function 
    # sheet - the xlwriter sheet on which the title is to be placed
    # predictors_data - full description of predictor 
    #                   which creared in update_predictors
    # format - format which will be used for header

    header_info = ""
    header_info +=   ('Column: ' + predictors_data['name'] + '\n' + 
                     'Type: '+  predictors_data['predictor_type'])
    sheet.merge_range("A1:K10", header_info , format)


def print_table_header(calling_obj, sheet, table, start_cell, head_text, header_bar_fromat):
    '''default method for add desctibe table on excel sheet'''
    # inputs:
    # calling_obj - object that called the function 
    # sheet - the xlwriter sheet on which the title is to be placed
    # table - pandas.DataFrame table to save
    # start_cell - str sell from which table will start
    # head_text - text which will dispalyed at the header
    # header_bar_fromat - bar which will be displayed above the table
    
    s_row, s_col = xl_cell_to_rowcol(start_cell)
    header_bar_range = (start_cell + ":" + 
                        xl_rowcol_to_cell(s_row, s_col + table.shape[1]))
    sheet.merge_range(header_bar_range, head_text, header_bar_fromat)
    table.to_excel(calling_obj.my_writer, sheet_name = sheet.name,
                    startrow = s_row+1, startcol = s_col)

def print_double_column_header( calling_obj, sheet, table, start_cell, 
                                head_text, header_bar_fromat):
    '''default funciton for printing classify ability indicators'''
    s_row, s_col = xl_cell_to_rowcol(start_cell)
    header_bar_range = (start_cell + ":" + 
                        xl_rowcol_to_cell(s_row, s_col + table.shape[1]))
    sheet.merge_range(header_bar_range, head_text, header_bar_fromat)
    save_double_column_df(table, calling_obj.my_writer, sheet_name = sheet.name,
                            startrow = s_row+1, startcol = s_col)



def default_predictor_printer(calling_obj, sheet, predictors_data, defatult_formats):
    # inputs:
    # calling_obj - object that called the function
    # sheet - the xlwriter sheet on which the title is to be placed
    # predictors_data - full description of predictor 
    #                   which creared in update_predictors
    # defatult_formats - formats which will be used be default

    calling_obj.header_printer(sheet, predictors_data, defatult_formats['header_format'])
    calling_obj.describe_table_printer( sheet, predictors_data['describe_table'], "A12",
                                        "Description", defatult_formats['desc_format'])
  
    calling_obj.class_ability_table_printer( sheet, 
                                        calling_obj.result_DF.loc[[predictors_data['name']],:],
                                        "M1", "Classification ability", 
                                        defatult_formats['class_ab_format'])