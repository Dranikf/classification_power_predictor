from xlsxwriter.utility import xl_cell_to_rowcol, xl_rowcol_to_cell

def add_sheet(xl_writer, sheet_name):
    '''Adding a sheet with setted name.
    Illegal characters will be removed.
    If name is too long it will be cutted.
    If there is same names they will be numerated.'''
    # inputs:
    # xl_writer - xlsx writer wich must contains new list
    # sheet_name -  desired name of creating sheet,
    #               it can be changed by method, in case
    #               incorrect symbols, too long name or
    #               recurring name  
        
    sheet_name = sheet_name.replace('/', ' ')
    sheet_name = sheet_name if len(sheet_name) < 31 else sheet_name[0:31]
        
    final_name = sheet_name
    i = 2
    # if the name is too long or repeating many times
    # its need spesical handle for this cases
    while final_name in xl_writer.sheets.keys():
        i_str = str(i)
        final_name = sheet_name + i_str

        if len(final_name) >= 32:
            final_name = final_name[0:(31-len(i_str))] + final_name[31:]

        i += 1
        
    result_sheet = xl_writer.book.add_worksheet(final_name)
    xl_writer.sheets[final_name] = result_sheet
        
    return final_name


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


def save_double_column_df(df, xl_writer, startrow = 0, **kwargs):
    '''Function to save doublecolumn DataFrame, to xlwriter'''
    # inputs:
    # df - pandas dataframe to save
    # xl_writer - book for saving
    # startrow - row from wich data frame will begins
    # **kwargs - arguments of `to_excel` function of DataFrame`
    df.drop(df.index).to_excel(xl_writer, startrow = startrow, **kwargs)
    df.to_excel(xl_writer, startrow = startrow + 1, header = False, **kwargs)

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