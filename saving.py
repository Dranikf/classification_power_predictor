# Функции ответсветвенные за сохранение результата анализа 
# классифицирующей способности предикторов в отдельный 
# Excel файл
from xlsxwriter.utility import xl_range, xl_cell_to_rowcol, xl_rowcol_to_cell

# формат заголовка для каждого листа - по умолчанию
header_format = {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#C0C0C0','font_size':15}
# то какую область займет заголовок
header_range = xl_range(0,0,5,10)
# формат заголовка к описательной таблице
desc_format = {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#C0C0C0','font_size':11}
# то от куда должна начинаться описательноая таблица (заранее не известно, где она закончиться)
desc_cell_start = "A9"
# формат заголовка к таблице метрик взаимосвязи
rel_head_format = {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#C0C0C0','font_size':11}
# то от куда должна начинаться таблица метри взаимосязи
rel_cell_start = "K9"


def add_sheet(xl_writer, sheet_name):
    '''Добавление листа с заданным именем в одну строчку.
    Притом учитывается что имена могут быть больше чем нужно
    потому в случае необходимости будут обрезаны с конца.
    Также предполагается замена недопустимых символов на пробелы'''
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

def create_sheet_by_df_col(xl_writer, df_name, col, col_ind):
    '''фнукция отвечает за то, чтобы в переданной книге создавались листы с правильным занванием
    соответствующим текущему набору данных и колонке'''
    
    # inputs:
    # xl_writer - созданная книга
    # df_name - имя набора данных обратываемого на данный момент
    # col - имя колонки, которая обрабатывается на данынй момент
    # col_ind - индекс колонки, которая обрабатывается на данный момент
    # output - имя новосозданного листа
    if df_name:
        sheet_name = 'дан.' + df_name + '_' + str(col_ind) + col
    else:
        sheet_name = col
    
    sheet_name = add_sheet(xl_writer, sheet_name)
    
    return sheet_name
    
    
def create_header(xl_writer, sheet_name, col, df_name, is_numeric, header_format, header_range):
    '''Создание заголовка описывающего переменную и его нанаесение на лист'''
    # inputs:
    # xl_writer - созданная книга
    # sheet_name - название листа
    # col - имя колонки которой посвящен лист
    # df_name - название data frame который обрабатывается
    # is_numeric - маркер, что даст понять численная ли переменная
    # header_format - формат ячеки заголовка
    # header_range - диапазон в который ляжет ячейка заголовок
    
    header_info = ""
    
    if df_name != None:
        header_info += 'Таблица: ' + df_name + '\n';
    
    header_info +=   ('Столбец: ' + col + '\n' + 
                     'Тип переменной: '+  ('Численная' if is_numeric else 'Номинативная'))
    xl_writer.sheets[sheet_name].merge_range(header_range, header_info , header_format)


def print_describe_table(xl_writer, sheet_name, table, header_format, start_cell):
    '''функция служит для того, чтобы поместить описательные статистики на лист Excel'''
    # inputs:
    # xl_writer - созданная книга
    # sheet_name - имя листа
    # table - таблица, которую следует поместить
    # header_format - формат заголовка
    # start_cell - адрес ячейки с которой начнется запись описательной статистики
    start_row_col = xl_cell_to_rowcol(start_cell)
    
    header_range = xl_range(start_row_col[0], start_row_col[1], start_row_col[0], start_row_col[1]+4)
    xl_writer.sheets[sheet_name].merge_range(header_range, "Описательная статистика" , header_format)
    
    table.to_excel(xl_writer, sheet_name = sheet_name, startrow=start_row_col[0] + 1 , startcol=start_row_col[1])
    
def print_rel_table(xl_writer, sheet_name, table, header_format, start_cell = rel_cell_start):
    start_row_col = xl_cell_to_rowcol(start_cell)
    
    header_range = xl_range(start_row_col[0], start_row_col[1], start_row_col[0], start_row_col[1]+6)
    xl_writer.sheets[sheet_name].merge_range(header_range, "Статистика взаимосвязи" , header_format)
    
    table.to_excel(xl_writer, sheet_name = sheet_name, startrow=start_row_col[0] + 1 , startcol=start_row_col[1], index=False)
    
    
def rgb_to_hex(rgb):
    '''преобразование RGB из десятичного формата в шеснадцатиричный'''
    # inputs:
    # rgb - (<r>,<g>,<b>)
    # outputs:
    # "rrggbb" (hex)
    return '%02x%02x%02x' % rgb

def get_rgb_from_linear_combin(value):
    '''Формирует цвет в формате RGB в виде линейной комбинации
    между зеленый->жёлтый->красный в привязке к value'''
    # inputs:
    # value - значение к которму будет привязываться лин. комб.
    # output:
    # (<r>,<g>,<b>)
    if value > 0.5:
        green_comp = 255
        red_comp = int((1-value)*255/0.5)
    if value <= 0.5:
        green_comp = int(value*255/0.5)
        red_comp = 255
    
    blue_comp = 0;
    
    return (red_comp, green_comp, blue_comp)

def r_y_g_color_by_linear_combin(sheet, value):
    '''фнукция проводит закрашивание "ярлычка" вкладки
    цеветовая гамма изменяется зеленый->желтый->красный '''
    # inputs:
    # sheet - лист ярлычек которого следует перекрасить
    # value - число от 0 до 1 которое будет основой 
    #         для линейной комбинации
    
    sheet.set_tab_color("#" + rgb_to_hex(get_rgb_from_linear_combin(value)))
    
def colorise_final(table):
    '''Принцип расскраски финальной таблицы'''
    # inputs:
    # table - таблица которую следует расскрасить
    # outputs:
    # styler - стилизованная таблица, которая будет 
    #          использована для сохранения
    
    def set_color(score, color):
        return f"background-color: " + color + ";"
    
    styler = table.style
    
    for i in table.index:
        
        value = table.loc[i, 'AUC'] - (table.loc[i, 'Доля пропусков%']/100)
        color_str = "#"+rgb_to_hex(get_rgb_from_linear_combin(value if value > 0 else 0))
        
        styler = styler.applymap(set_color, subset=(i, slice(None)), color = color_str)
        
    return styler


def filter_adding(sheet):
    '''Добаваление и настройка фильтра на лист резульатата'''
    sheet.autofilter(0,0,0,12)
    #sheet.filter_column_list("M", [0])
    
    