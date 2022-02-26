from factors_research.saving import *
from factors_research.computions import *


#class fac_stats_book():
#    '''Класс реализует книгу для создания '''   
#    def 



def create_book(dfs, y_col, res_book_name, df_names = None, header_format = header_format,
                header_range = header_range, desc_format = desc_format, 
                desc_cell_start = desc_cell_start, rel_head_format = rel_head_format,
                rel_cell_start = rel_cell_start, nominal_drop_cirteria = None):
    # inputs:
    # dfs - лист содержащий таблицы с данными
    # y_col - столбцы отклика (list) 
    # res_book_name - название книги результата
    # df_names - имена которые будут присвоены по наборам данных
    # header_format - формат ячеки заголовка
    # header_range - диапазон в который ляжет ячейка заголовок
    # desc_format - формат заголовка описательных статистик
    # desc_cell_start - ячейка с которой начинается область описательных статистик
    # rel_head_format - формат загловка метрик взаимосвязи
    # rel_cell_start - ячейка с которой начинается обсласть статистик взаимосвязи
    # nominal_drop_criteria - 
    
    df_names = df_names if df_names else ['Данные ' + str(i) for i in range(len(dfs))]
    xl_writer = pd.ExcelWriter(res_book_name,engine='xlsxwriter')
    header_format = xl_writer.book.add_format(header_format)
    desc_format = xl_writer.book.add_format(desc_format)
    rel_head_format = xl_writer.book.add_format(rel_head_format)
    
    final_table = pd.DataFrame()
    
    for df_ind, df in enumerate(dfs):
        for col_ind, col in enumerate(df.columns):
            
            if (sum(df[col].isna()) / df.shape[0]) >= 0.3:
                continue
            
            # получим числовой ли предиктор рассматривается
            is_numeric = np.isin(np.fromiter(map(str, df.dtypes.to_numpy()), dtype='S128')[col_ind], [b'int64', b'float64'])
            # инициализация листа
            curr_sheet_N = create_sheet_by_df_col(xl_writer, df_names[df_ind], col, col_ind)
            create_header(xl_writer, curr_sheet_N, col, df_names[df_ind], is_numeric, header_format, header_range)
            
            # проведение вычислительной процедуры
            comp_res = computions_fun(df[col], y_col[df_ind], is_numeric)
            
            # полседовательная запись информации на листы
            print_describe_table(xl_writer, curr_sheet_N, comp_res['discribe_table'], desc_format, desc_cell_start)
            disc_table = comp_res['discribe_table'].copy()
            del comp_res["discribe_table"]
            comp_res = pd.DataFrame([comp_res])
            print_rel_table(xl_writer, curr_sheet_N, comp_res, rel_head_format, rel_cell_start)
            r_y_g_color_by_linear_combin(xl_writer.sheets[curr_sheet_N], ((comp_res['AUC'] - 0.5)/0.5).iat[0])
            
            
            comp_res['Название предиктора'] = col
            if df_names[df_ind]:
                comp_res['Таблица содержания'] = df_names[df_ind]
            
            
            comp_res['Подлежит укрупнению'] = False
            # для номинативного предиктора следует проверить не является ли он очень разряженным (подлежащим)
            # укрупнению - если это так то его следует как минимум пометить
            if not is_numeric:
                if disc_table['Число'].mean() < 20:
                    comp_res['Подлежит укрупнению'] = True
            
            # запись целого DataFrame для того, чтобы вывести его на последний лист
            final_table = pd.concat([final_table, comp_res])
            
            

    if df_names[df_ind]:
        final_table.set_index(["Название предиктора",'Таблица содержания'], inplace = True)
    else:
        final_table.set_index(["Название предиктора"], inplace = True)
        
    
    final_table.sort_values("AUC", inplace = True, ascending=False)
    
    save_table = colorise_final(final_table)
    save_table.to_excel(xl_writer, sheet_name = "РЕЗУЛЬТАТ")
    filter_adding(xl_writer.sheets["РЕЗУЛЬТАТ"])
    
    xl_writer.close()