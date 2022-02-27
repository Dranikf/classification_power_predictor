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


def default_header_creator(calling_obj ,sheet, predictors_data, default_format):
    '''Создание заголовка описывающего переменную и его нанаесение на лист'''
    # inputs:
    # col - имя колонки которой посвящен лист
    # df_name - название data frame который обрабатывается
    # is_numeric - маркер, что даст понять численная ли переменная
    # header_format - формат ячеки заголовка
    # header_range - диапазон в который ляжет ячейка заголовок
    
    header_info = ""
    header_info +=   ('Column: ' + predictors_data['name'] + '\n' + 
                     'Type: '+  predictors_data['predictor_type'])
    sheet.merge_range("A1:K10", header_info , default_format)