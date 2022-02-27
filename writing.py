def add_sheet(xl_writer, sheet_name):
    '''Adding a sheet with setted name.
    Illegal characters will be removed.
    If name is too long it will be cutted.
    If there is same names they will be numerated.'''
    # inputs:
    # xl_writer - книга на которую надо добавить лист
    # sheet_name - название создаваемого листа
        
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