import os  # импорт библиотек
from datetime import datetime
from meteostat import Point
from meteostat import Daily
from windrose import WindroseAxes
import tkinter as tk
import tkinter.ttk as ttk
import pandas as pd
from pandastable import Table
import numpy as np
from tkinter import filedialog as fd
from tkinter import messagebox as mb 
import tkinter.font as tkFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('fast')  # стиль графиков


def import_file():
    """Функция импорта файла и его обработки для правильной работы функций"""
    global file_name, climate
    file_name= fd.askopenfilename(filetypes=(("Файлы Excel(XLSX) или CSV", ("*.xlsx", ".csv")), ("Все файлы", "*.*")))
    file_chosen_label['text'] = 'Файл "{}" выбран'.format(file_name.split('/')[-1])
    file_chosen_label['foreground']='green'
    filename, file_extension = os.path.splitext(file_name)
    if file_extension == '.xlsx':
            starting_row = find_starting_row_xlsx(file_name, "Дата")
            climate = pd.read_excel(file_name, skiprows=starting_row, index_col='Дата', parse_dates=True)
    elif file_extension == '.csv':
            starting_row = find_starting_row_csv(file_name, "Дата")
            climate = pd.read_csv(file_name, skiprows=starting_row, delimiter=';',
                                  index_col='Дата', encoding='cp1251', parse_dates=True)
    climate = climate.apply(pd.to_numeric, errors='coerce', axis=1)
    climate = climate.replace(9999, np.nan)
    climate.index = pd.to_datetime(climate.index, format='%d.%m.%Y')
    # Создаем новый DataFrame с пропущенными значениями заполненными nan
    all_dates_1980_2020 = pd.date_range(start='1960-01-01', end='2020-12-31', freq='D')
    climate = climate.reindex(all_dates_1980_2020)
    return climate
    
    
def find_starting_row_xlsx(file_name, target_cell_value):
    """Функция поиска первой строки в файле XLSX"""
    df = pd.read_excel(file_name, header=None)
    for idx, row in df.iterrows():
        if target_cell_value in row.values:
            return idx
    return 0  # Если строка не найдена, начать с первой строки


def find_starting_row_csv(file_name, target_cell_value):
    """Функция поиска первой строки в файле CSV"""
    df = pd.read_csv(file_name, delimiter=';', encoding='cp1251', header=None)
    for idx, row in df.iterrows():
        if target_cell_value in row.values:
            return idx
    return 0  # Если строка не найдена, начать с первой строки


def separate_climate(climate_data):
    """Разделение таблицы по колонкам параметров"""
    max_temp_climate = climate_data.iloc[:, :1]
    min_temp_climate = climate_data.iloc[:, 1:2]
    mean_temp_climate = climate_data.iloc[:, 2:3]
    pressure_climate = climate_data.iloc[:, 3:4]
    wind_climate = climate_data.iloc[:, 4:5]
    precipitation_climate = climate_data.iloc[:, 5:6]
    eff_temp_climate = climate_data.iloc[:, 6:7]
    
    return (max_temp_climate, min_temp_climate, mean_temp_climate, pressure_climate, wind_climate, precipitation_climate, eff_temp_climate)


def add_fig():
    """Создание окна с результатами нажатия кнопок"""
    global fig
    fig = tk.Toplevel()
    fig.geometry('{}x{}+{}+0'.format(w*2, h, w))
    fig.wm_iconbitmap('climate.ico')
    return fig


def add_frames():
    """Создание рамки со скроллбарами"""
    global second_frame


    def on_mousewheel(event):
        my_canvas.yview_scroll(-1 * (event.delta // 120), "units")


    main_frame=tk.Frame(fig)
    main_frame.pack(fill=tk.BOTH, expand=1)

    sec = tk.Frame(main_frame)
    sec.pack(fill=tk.X, side=tk.BOTTOM)

    my_canvas = tk.Canvas(main_frame)
    my_canvas.pack(side=tk.LEFT, fill=tk.BOTH,expand=1)

    x_scrollbar = ttk.Scrollbar(sec,orient=tk.HORIZONTAL,command=my_canvas.xview)
    x_scrollbar.pack(side=tk.BOTTOM,fill=tk.X)

    y_scrollbar = ttk.Scrollbar(main_frame,orient=tk.VERTICAL,command=my_canvas.yview)
    y_scrollbar.pack(side=tk.RIGHT,fill=tk.Y)

    my_canvas.configure(xscrollcommand=x_scrollbar.set)
    my_canvas.configure(yscrollcommand=y_scrollbar.set)
    my_canvas.bind("<Configure>",lambda e: my_canvas.config(scrollregion= my_canvas.bbox(tk.ALL))) 
    fig.bind("<MouseWheel>", on_mousewheel)

    second_frame = tk.Frame(my_canvas)
    my_canvas.create_window((5,5),window= second_frame, anchor="nw")
    return second_frame


def add_canvas(graphs):
    """Создание холста с панелью инструментов для графиков"""
    global canvas
    
    
    def add_toolbar():
        global toolbar
        toolbar = NavigationToolbar2Tk(canvas, second_frame)  #управление графиками
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.BOTH)


    canvas = FigureCanvasTkAgg(graphs, second_frame)  #холст
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, expand=True)
    add_toolbar()


def table_climate():
    """Таблица данных"""
    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
    
    add_fig()
    fig.title('Таблица данных "{}"'.format(file_name.split('/')[-1]))
    
    frame = tk.Frame(fig)
    frame.pack(fill='both', expand=True)

    pt = Table(frame, showtoolbar=True, showstatusbar=True, dataframe=climate)
    pt.show()


def raschet():
    """Статистические характеристики"""

    def math_stat(parameter):
        global second_frame
        ttk.Label(second_frame, text =  parameter.columns[0], font=tkFont.Font(family='Calibri',size=14)).pack()
        ttk.Label(second_frame, text =  'Математическое ожидание = ' + "%.2f" % parameter.iloc[:,0].mean()).pack()
        ttk.Label(second_frame, text =  'Дисперсия = ' + "%.2f" % parameter.iloc[:,0].std() ** 2).pack() 
        ttk.Label(second_frame, text =  'Среднеквадратическое отклонение = ' + "%.2f" % parameter.iloc[:,0].std()).pack() 
        ttk.Label(second_frame, text =  'Наименьшее значение = ' + "%.2f" % parameter.iloc[:,0].min()).pack()
        ttk.Label(second_frame, text =  'Наибольшее значение = ' + "%.2f" % parameter.iloc[:,0].max()).pack()
        ttk.Label(second_frame, text =  'Ошибка средней арифметической = ' + "%.2f" % (parameter.iloc[:,0].std()/parameter.iloc[:,0].count() ** 0.5)).pack()
        ttk.Label(second_frame, text =  'Коэффициент вариации = ' + "%.2f" % (parameter.iloc[:,0].std()/parameter.iloc[:,0].mean() * 100) + ' %' + '\n').pack()

    def export_to_file():
        global stat_file

        def print_climate(parameter):
            stat_file.write(f'{parameter.columns[0]}:' + '\n')
            stat_file.write("Математическое ожидание = " + "%.2f" % parameter.iloc[:,0].mean() + ';\n')
            stat_file.write('Дисперсия = ' + "%.2f" % parameter.iloc[:,0].std() ** 2 + ';\n')
            stat_file.write('Среднеквадратическое отклонение = ' + "%.2f" % parameter.iloc[:,0].std() + ';\n')
            stat_file.write('Наименьшее значение = ' + "%.2f" % parameter.iloc[:,0].min() + ';\n')
            stat_file.write('Наибольшее значение = ' + "%.2f" % parameter.iloc[:,0].max() + ';\n')
            stat_file.write('Ошибка средней арифметической = ' + "%.2f" % (parameter.iloc[:,0].std()/parameter.iloc[:,0].count() ** 0.5) + ';\n')
            stat_file.write('Коэффициент вариации = ' + "%.2f" % (parameter.iloc[:,0].std()/parameter.iloc[:,0].mean() * 100) + ' %' + ';\n' + '\n')

        time = datetime.now().strftime('%Y-%m-%d')
        stat_file = open(f"Files\{time} - {file_name.split('/')[-1].split('.')[0]}.txt", "w+")
        for parameter in result:
            print_climate(parameter)
        stat_file.close()

    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
        
    result = separate_climate(climate)

    add_fig()
    fig.title('Статистические характеристики "{}"'.format(file_name.split('/')[-1]))

    add_frames()

    ttk.Label(second_frame, text='Статистические характеристики "{}" \n'.format(file_name.split('/')[-1]),
              font=tkFont.Font(family='Calibri',size=18)).pack()

    # Вычисление и отображение статистических характеристик
    for parameter in result:
        math_stat(parameter)

    ttk.Button(second_frame, text = 'Сохранить в файл', command = export_to_file).pack()


def selected_raschet():
    """Статистические характеристики в указанном диапазоне дат"""

    def math_stat(parameter):
        global second_frame
        ttk.Label(second_frame, text =  parameter.columns[0], font=tkFont.Font(family='Calibri',size=14)).pack()
        ttk.Label(second_frame, text =  'Математическое ожидание = ' + "%.2f" % parameter.iloc[:,0].mean()).pack()
        ttk.Label(second_frame, text =  'Дисперсия = ' + "%.2f" % parameter.iloc[:,0].std() ** 2).pack() 
        ttk.Label(second_frame, text =  'Среднеквадратическое отклонение = ' + "%.2f" % parameter.iloc[:,0].std()).pack() 
        ttk.Label(second_frame, text =  'Наименьшее значение = ' + "%.2f" % parameter.iloc[:,0].min()).pack()
        ttk.Label(second_frame, text =  'Наибольшее значение = ' + "%.2f" % parameter.iloc[:,0].max()).pack()
        ttk.Label(second_frame, text =  'Ошибка средней арифметической = ' + "%.2f" % (parameter.iloc[:,0].std()/parameter.iloc[:,0].count() ** 0.5)).pack()
        ttk.Label(second_frame, text =  'Коэффициент вариации = ' + "%.2f" % (parameter.iloc[:,0].std()/parameter.iloc[:,0].mean() * 100) + ' %' + '\n').pack()


    def export_to_file():
        global stat_file
        def print_climate(parameter):
            stat_file.write(f'{parameter.columns[0]}:' + '\n')
            stat_file.write("Математическое ожидание = " + "%.2f" % parameter.iloc[:,0].mean() + ';\n')
            stat_file.write('Дисперсия = ' + "%.2f" % parameter.iloc[:,0].std() ** 2 + ';\n')
            stat_file.write('Среднеквадратическое отклонение = ' + "%.2f" % parameter.iloc[:,0].std() + ';\n')
            stat_file.write('Наименьшее значение = ' + "%.2f" % parameter.iloc[:,0].min() + ';\n')
            stat_file.write('Наибольшее значение = ' + "%.2f" % parameter.iloc[:,0].max() + ';\n')
            stat_file.write('Ошибка средней арифметической = ' + "%.2f" % (parameter.iloc[:,0].std()/parameter.iloc[:, 0].count() ** 0.5) + ';\n')
            stat_file.write('Коэффициент вариации = ' + "%.2f" % (parameter.iloc[:,0].std()/parameter.iloc[:,0].mean() * 100) + ' %' + ';\n' + '\n')


        time = datetime.now().strftime('%Y-%m-%d')
        stat_file = open(f"Files\{time} - {file_name.split('/')[-1].split('.')[0]} ({first_date}) - ({second_date}).txt", "w+")
        for parameter in result:
            print_climate(parameter)
        stat_file.close()

    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return

    result = separate_climate(climate)

    first_date = '{}-{}-{}'.format(combobox_start_years.get(), combobox_start_months.get(), combobox_start_days.get())
    second_date = '{}-{}-{}'.format(combobox_finish_years.get(), combobox_finish_months.get(), combobox_finish_days.get())

    try:
        add_fig()
        fig.title('Статистические характеристики в указанном диапазоне дат ({} - {}) "{}"'.format(first_date, second_date, file_name.split('/')[-1]))

        add_frames()

        ttk.Label(second_frame, text='Статистические характеристики в указанном диапазоне дат ({} - {}) "{}" '.format(first_date, second_date, file_name.split('/')[-1]),
                    font=tkFont.Font(family='Calibri',size=18)).pack()
        for parameter in result:
            math_stat(parameter.loc[first_date:second_date])

        ttk.Button(second_frame, text = 'Сохранить в файл', command = export_to_file).pack()
    except:
            fig.destroy()
            mb.showerror("Ошибка", "Не выбран диапазон дат")


def graph_climate():
    """Построение графиков распределения"""

    def plot_climate(parameter):
        graphs = Figure(figsize=size, dpi = 100)
        ax = graphs.add_subplot(1,1,1)
        ax.plot(parameter, 'o', markersize = 1, label = parameter.columns[0], alpha = 0.5)       
        ax.set_title(parameter.columns[0])
        graphs.autofmt_xdate()
        add_canvas(graphs)


    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
      
    # Разделение данных климата
    result = separate_climate(climate)

    add_fig()
    fig.title('Графики распределения климатических характеристик "{}"'.format(file_name.split('/')[-1]))

    add_frames()

    ttk.Label(second_frame, text =  'Графики распределения климатических характеристик "{}" \n'.format(file_name.split('/')[-1]), 
                font=tkFont.Font(family='Calibri',size=32)).pack()

    for parameter in result:
        plot_climate(parameter)


def histo_climate():
    """Построение гистограм плотсноти распределения"""

    def hist_climate(parameter):
        kwargs = dict(bins = 60, histtype = 'stepfilled', alpha=0.5, edgecolor='black')
        graphs = Figure(figsize=size, dpi = 100)
        ax = graphs.add_subplot(1,1,1)
        ax.hist(parameter, **kwargs)
        ax.minorticks_on()
        ax.xaxis.set_minor_locator(mticker.MultipleLocator(base=1.))
        ax.grid(True)
        ax.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
        ax.set_title(parameter.columns[0])
        ax.set_ylabel('Плотность, N раз')
        add_canvas(graphs)

    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
        
    # Разделение данных климата
    result = separate_climate(climate)
        
    add_fig()
    fig.title('Гистограммы плотности распределения климатических характеристик "{}"'.format(file_name.split('/')[-1]))
    
    add_frames()

    ttk.Label(second_frame, text =  'Гистограммы плотности распределения климатических характеристик "{}" \n'.format(file_name.split('/')[-1]), font=tkFont.Font(family='Calibri',size=32)).pack()

    for parameter in result:
        hist_climate(parameter)


def kde_climate():
    """Построение графиков плотности распределения"""

    def kde_parameter(parameter):
        graphs = Figure(figsize=size, dpi = 100)
        ax = graphs.add_subplot(1,1,1)
        sns.kdeplot(parameter.squeeze(), ax=ax, linewidth=1)
        ax.minorticks_on()
        ax.xaxis.set_minor_locator(mticker.MultipleLocator(base=1.))
        ax.grid(True)
        ax.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
        ax.set_title(parameter.columns[0])
        ax.set_ylabel('Плотность')
        add_canvas(graphs)
        
    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
        
    # Разделение данных климата
    result = separate_climate(climate)
        
    add_fig()
    fig.title('Графики плотности распределения климатических характеристик "{}"'.format(file_name.split('/')[-1]))
    
    add_frames()

    ttk.Label(second_frame, text =  'Графики плотности распределения климатических характеристик "{}" \n'.format(file_name.split('/')[-1]), font=tkFont.Font(family='Calibri',size=32)).pack()
    
    graphs1 = Figure(figsize=size, dpi = 100)
    ax1 = graphs1.add_subplot(1,1,1)
    sns.kdeplot(result[0].squeeze(), ax=ax1, color='r', label = 'Максимальная температура', linewidth=1)
    sns.kdeplot(result[1].squeeze(), ax=ax1, color='b', label = 'Минимальная температура', linewidth=1)
    sns.kdeplot(result[2].squeeze(), ax=ax1, color = 'g', label = 'Средняя температура', linewidth=1)
    
    ax1.minorticks_on()
    ax1.xaxis.set_minor_locator(mticker.MultipleLocator(base=1.))
    ax1.grid(True)
    ax1.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
    ax1.set_title('Температура')
    ax1.set_ylabel('Плотность')
    ax1.set_xlabel('Температура')
    ax1.legend(loc='best', ncol=3)
    add_canvas(graphs1)

    kde_parameter(result[3])
    kde_parameter(result[4])
    kde_parameter(result[5])
    kde_parameter(result[6])


def kde_selected_climate():
    """Построение графиков плотности распределения в указанном диапазоне"""

    def kde_selected_parameter(parameter):
        graphs = Figure(figsize=size, dpi = 100)
        ax = graphs.add_subplot(1,1,1)
        sns.kdeplot(parameter.loc[first_date:second_date].squeeze(), ax=ax, linewidth=1)
        ax.minorticks_on()
        ax.xaxis.set_minor_locator(mticker.MultipleLocator(base=1.))
        ax.grid(True)
        ax.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
        ax.set_title(parameter.columns[0])
        ax.set_ylabel('Плотность')
        add_canvas(graphs)
        
    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
        
    # Разделение данных климата
    result = separate_climate(climate)

    first_date = '{}-{}-{}'.format(combobox_start_years.get(), combobox_start_months.get(), combobox_start_days.get())
    second_date = '{}-{}-{}'.format(combobox_finish_years.get(), combobox_finish_months.get(), combobox_finish_days.get())
        
    try:
        add_fig()
        fig.title('Графики плотности распределения климатических параметров в указанном диапазоне дат ({} - {}) "{}"'.format(first_date, second_date, file_name.split('/')[-1]))
        
        add_frames()

        ttk.Label(second_frame, text =  'Графики плотности распределения климатических параметров в указанном диапазоне дат ({} - {}) "{}"'.format(first_date, second_date, file_name.split('/')[-1]), 
                    font=tkFont.Font(family='Calibri',size=24)).pack()
        
        graphs1 = Figure(figsize=size, dpi = 100)
        ax1 = graphs1.add_subplot(1,1,1)
        sns.kdeplot(result[0].loc[first_date:second_date].squeeze(), ax=ax1, color='r', label = 'Максимальная температура', linewidth=1)
        sns.kdeplot(result[1].loc[first_date:second_date].squeeze(), ax=ax1, color='b', label = 'Минимальная температура', linewidth=1)
        sns.kdeplot(result[2].loc[first_date:second_date].squeeze(), ax=ax1, color = 'g', label = 'Средняя температура', linewidth=1)
        
        ax1.minorticks_on()
        ax1.xaxis.set_minor_locator(mticker.MultipleLocator(base=1.))
        ax1.grid(True)
        ax1.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
        ax1.set_title('Температура')
        ax1.set_ylabel('Плотность')
        ax1.set_xlabel('Температура')
        ax1.legend(loc='best', ncol=3)
        add_canvas(graphs1)

        for i in range(3,7):
            kde_selected_parameter(result[i])

    except:
        fig.destroy()
        mb.showerror("Ошибка", "Не выбран диапазон дат")


def graph_selected_climate():
    """Построение графиков в указанном диапазоне дат"""

    def graph_selected_paramater(parameter):
        graphs = Figure(figsize=size, dpi = 100)
        ax = graphs.add_subplot(1,1,1)
        ax.plot(parameter.loc[first_date:second_date], label = parameter.columns[0], linewidth=1)
        ax.minorticks_on()
        ax.grid(True)
        ax.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
        ax.set_title(parameter.columns[0])
        add_canvas(graphs)


    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
        
    # Разделение данных климата
    max_temp_climate, min_temp_climate, mean_temp_climate, pressure_climate, wind_climate, precipitation_climate, eff_temp_climate= separate_climate(climate)
        
    first_date = '{}-{}-{}'.format(combobox_start_years.get(), combobox_start_months.get(), combobox_start_days.get())
    second_date = '{}-{}-{}'.format(combobox_finish_years.get(), combobox_finish_months.get(), combobox_finish_days.get())

    try:
        add_fig()
        fig.title('Графики распределения климатических характеристик в указанном диапазоне дат ({} - {}) "{}"'.format(first_date, second_date, file_name.split('/')[-1]))
        
        add_frames()

        ttk.Label(second_frame, text =  'Графики распределения климатических характеристик в указанном диапазоне дат ({} - {}) "{}"'.format(first_date, second_date, file_name.split('/')[-1]), 
                    font=tkFont.Font(family='Calibri',size=24)).pack()
        
        graphs1 = Figure(figsize=size, dpi = 100)
        ax1 = graphs1.add_subplot(1,1,1)
        ax1.plot(mean_temp_climate.loc[first_date:second_date], 'g', label = 'Средняя температура', alpha = 0.5, linewidth=1)
    except:
        fig.destroy()
        mb.showerror("Ошибка", "Не выбран диапазон дат")
    else:
            ax1.plot(max_temp_climate.loc[first_date:second_date], 'r', label = 'Максимальная температура', alpha = 0.5, linewidth=1)
            ax1.plot(min_temp_climate.loc[first_date:second_date], 'b', label = 'Минимальная температура', alpha = 0.5, linewidth=1)
            ax1.minorticks_on()
            ax1.grid(True)
            ax1.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
            ax1.set_title('Температура')
            ax1.legend(loc='best', ncol=3)
            add_canvas(graphs1)

            graph_selected_paramater(pressure_climate)
            graph_selected_paramater(wind_climate)
            graph_selected_paramater(precipitation_climate)
            graph_selected_paramater(eff_temp_climate)


def histo_selected_climate():
    """Построение гистограм плотности распределения в указанном диапазоне дат"""

    def histo_selected_parameter(parameter):
        graphs = Figure(figsize=size, dpi = 100)
        ax = graphs.add_subplot(1,1,1)
        ax.hist(parameter.loc[first_date:second_date], **kwargs)
        ax.minorticks_on()
        ax.xaxis.set_minor_locator(mticker.MultipleLocator(base=1.))
        ax.grid(True)
        ax.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
        ax.set_title(parameter.columns[0])
        ax.set_ylabel('Плотность, N раз')
        add_canvas(graphs)


    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
        
    # Разделение данных климата
    max_temp_climate, min_temp_climate, mean_temp_climate, pressure_climate, wind_climate, precipitation_climate, eff_temp_climate= separate_climate(climate)

    first_date = '{}-{}-{}'.format(combobox_start_years.get(), combobox_start_months.get(), combobox_start_days.get())
    second_date = '{}-{}-{}'.format(combobox_finish_years.get(), combobox_finish_months.get(), combobox_finish_days.get())
        
    try:
        add_fig()
        fig.title('Гистограммы плотности распределения климатических параметров в указанном диапазоне дат ({} - {}) "{}"'.format(first_date, second_date, file_name.split('/')[-1]))
        
        add_frames()

        ttk.Label(second_frame, text =  'Гистограммы плотности распределения климатических параметров в указанном диапазоне дат ({} - {}) "{}"'.format(first_date, second_date, file_name.split('/')[-1]), 
                    font=tkFont.Font(family='Calibri',size=24)).pack()

        kwargs = dict(bins = 60, histtype = 'stepfilled', alpha=0.5, edgecolor='black')

        graphs1 = Figure(figsize=size, dpi = 100)
        ax1 = graphs1.add_subplot(1,1,1)
        ax1.hist(max_temp_climate.loc[first_date:second_date], **kwargs)
    except:
        fig.destroy()
        mb.showerror("Ошибка", "Не выбран диапазон дат")
    else:
            ax1.minorticks_on()
            ax1.xaxis.set_minor_locator(mticker.MultipleLocator(base=1.))
            ax1.grid(True)
            ax1.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
            ax1.set_title(max_temp_climate.columns[0])
            ax1.set_ylabel('Плотность, N раз')
            add_canvas(graphs1)

            histo_selected_parameter(min_temp_climate)
            histo_selected_parameter(mean_temp_climate)
            histo_selected_parameter(pressure_climate)
            histo_selected_parameter(wind_climate)
            histo_selected_parameter(precipitation_climate)
            histo_selected_parameter(eff_temp_climate)


def graph_year_climate():
    """Построение графиков среднегодичных"""

    def graph_year_parameter(parameter):
        graphs = Figure(figsize=size, dpi = 100)
        ax = graphs.add_subplot(1,1,1)
        ax.plot(parameter, markersize = 1, linewidth=1)
        for i_x, i_y in zip(parameter.index, parameter.iloc[:,0]):
            ax.text(i_x, i_y, '({})'.format("%.1f" % i_y), fontsize=10)
        ax.minorticks_on()
        ax.grid(True)
        ax.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
        ax.set_title(parameter.columns[0])
        add_canvas(graphs)


    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
        
    year_climate = climate.resample('A').mean()
        # Разделение данных климата
    max_temp_climate, min_temp_climate, mean_temp_climate, pressure_climate, wind_climate, precipitation_climate, eff_temp_climate= separate_climate(year_climate)
        
    add_fig()
    fig.title('Графики распределения среднегодовых значений климатических параметров "{}"'.format(file_name.split('/')[-1]))

    add_frames()

    ttk.Label(second_frame, text =  'Графики распределения среднегодовых значений климатических параметров "{}"'.format(file_name.split('/')[-1]), 
                font=tkFont.Font(family='Calibri',size=32)).pack()

    graphs1 = Figure(figsize=size, dpi = 100)
    ax1 = graphs1.add_subplot(1,1,1)
    ax1.plot(mean_temp_climate, markersize = 1, label = 'Средняя температура', alpha = 0.5, linewidth=1)
    for i_x, i_y in zip(mean_temp_climate.index, mean_temp_climate.iloc[:,0]):
        ax1.text(i_x, i_y, '({})'.format("%.1f" % i_y), fontsize=10)
    ax1.plot(max_temp_climate, markersize = 1,label = 'Максимальная температура', alpha = 0.5, linewidth=1)
    for i_x, i_y in zip(max_temp_climate.index, max_temp_climate.iloc[:,0]):
        ax1.text(i_x, i_y, '({})'.format("%.1f" % i_y), fontsize=10)
    ax1.plot(min_temp_climate, markersize = 1, label = 'Минимальная температура', alpha = 0.5, linewidth=1)
    for i_x, i_y in zip(min_temp_climate.index, min_temp_climate.iloc[:,0]):
        ax1.text(i_x, i_y, '({})'.format("%.1f" % i_y), fontsize=10)
    ax1.minorticks_on()
    ax1.grid(True)
    ax1.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
    ax1.set_title('Температура')
    ax1.legend(loc='best', ncol=3)
    add_canvas(graphs1)

    graph_year_parameter(pressure_climate)
    graph_year_parameter(wind_climate)
    graph_year_parameter(precipitation_climate)
    graph_year_parameter(eff_temp_climate)


def graph_month_climate():
    """Построение графиков среднемесячных"""

    def graph_month_parameter(parameter):
        graphs = Figure(figsize=size, dpi = 100)
        ax = graphs.add_subplot(1,1,1)
        ax.plot(parameter, markersize = 1,  linewidth=1)
        ax.minorticks_on()
        ax.grid(True)
        ax.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
        ax.set_title(parameter.columns[0])
        add_canvas(graphs)


    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
        
    months_climate = climate.resample('M').mean()
    
    # Разделение данных климата
    max_temp_climate, min_temp_climate, mean_temp_climate, pressure_climate, wind_climate, precipitation_climate, eff_temp_climate= separate_climate(months_climate)
        
    add_fig()
    fig.title('Графики распределения среднемесячных значений климатических параметров "{}"'.format(file_name.split('/')[-1]))

    add_frames()

    ttk.Label(second_frame, text =  'Графики распределения среднемесячных значений климатических параметров "{}"'.format(file_name.split('/')[-1]), 
                font=tkFont.Font(family='Calibri',size=32)).pack()

    graph_month_parameter(max_temp_climate)
    graph_month_parameter(min_temp_climate)
    graph_month_parameter(mean_temp_climate)
    graph_month_parameter(pressure_climate)
    graph_month_parameter(wind_climate)
    graph_month_parameter(precipitation_climate)
    graph_month_parameter(eff_temp_climate)


def graph_selected_month_climate():
    """Построение графиков среднемесячных в указанном диапазоне"""

    def graph_selected_month_parameter(parameter):
        graphs = Figure(figsize=size, dpi = 100)
        ax = graphs.add_subplot(1,1,1)
        ax.plot(pressure_climate.loc[first_date:second_date], linewidth=1)
        ax.minorticks_on()
        ax.grid(True)
        ax.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
        ax.set_title(parameter.columns[0])
        add_canvas(graphs)


    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
        
    months_climate = climate.resample('M').mean()
    
    # Разделение данных климата
    max_temp_climate, min_temp_climate, mean_temp_climate, pressure_climate, wind_climate, precipitation_climate, eff_temp_climate= separate_climate(months_climate)
        
    first_date = '{}-{}-{}'.format(combobox_start_years.get(), combobox_start_months.get(), combobox_start_days.get())
    second_date = '{}-{}-{}'.format(combobox_finish_years.get(), combobox_finish_months.get(), combobox_finish_days.get())

    try:
        add_fig()
        fig.title('Графики распределения среднемесячных значений климатических параметров в указанном диапазоне дат ({} - {}) "{}"'.format(first_date, second_date, file_name.split('/')[-1]))
        
        add_frames()

        ttk.Label(second_frame, text =  'Графики распределения среднемесячных значений климатических параметров в указанном диапазоне дат ({} - {}) "{}"'.format(first_date, second_date, file_name.split('/')[-1]), 
                font=tkFont.Font(family='Calibri',size=24)).pack()
        
        graphs1 = Figure(figsize=size, dpi = 100)
        ax1 = graphs1.add_subplot(1,1,1)
        ax1.plot(mean_temp_climate.loc[first_date:second_date], 'g', label = 'Средняя температура', alpha = 0.5, linewidth=1)
    except:
        fig.destroy()
        mb.showerror("Ошибка", "Не выбран диапазон дат")
    else:
            ax1.plot(max_temp_climate.loc[first_date:second_date], 'r', label = 'Максимальная температура', alpha = 0.5, linewidth=1)
            ax1.plot(min_temp_climate.loc[first_date:second_date], 'b', label = 'Минимальная температура', alpha = 0.5, linewidth=1)
            ax1.minorticks_on()
            ax1.grid(True)
            ax1.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
            ax1.set_title('Температура')
            ax1.legend(loc='best', ncol=3)
            add_canvas(graphs1)

            graph_selected_month_parameter(pressure_climate)
            graph_selected_month_parameter(wind_climate)
            graph_selected_month_parameter(precipitation_climate)
            graph_selected_month_parameter(eff_temp_climate)
           
        
def graph_mean_months():
    """Построение графиков средних по месяцам"""

    def graph_mean_parameter(parameter):
        by_month_parameter = parameter.groupby(parameter.index.month).mean()
        by_month_parameter.index = mean_index
        graphs = Figure(figsize=size, dpi = 100)
        ax = graphs.add_subplot(1,1,1)
        ax.plot(by_month_parameter, '-o', linewidth=1)
        for i_x, i_y in zip(by_month_parameter.index, by_month_parameter.iloc[:,0]):
            ax.text(i_x, i_y, '({})'.format("%.1f" % i_y))
        ax.minorticks_on()
        ax.grid(True)
        ax.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
        ax.set_title(by_month_parameter.columns[0])
        add_canvas(graphs)


    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
        
    climate_months = climate.resample('M').mean()
    
    # Разделение данных климата
    max_temp_climate, min_temp_climate, mean_temp_climate, pressure_climate, wind_climate, precipitation_climate, eff_temp_climate= separate_climate(climate_months)
        
    add_fig()
    fig.title('Графики распределения среднемесячных значений климатических параметров "{}"'.format(file_name.split('/')[-1]))

    add_frames()

    ttk.Label(second_frame, text =  'Графики распределения среднемесячных значений климатических параметров "{}"'.format(file_name.split('/')[-1]), 
                font=tkFont.Font(family='Calibri',size=32)).pack()

    mean_index = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']

    by_month_meantemp = mean_temp_climate.groupby(mean_temp_climate.index.month).mean()
    by_month_meantemp.index = mean_index

    by_month_maxtemp = max_temp_climate.groupby(max_temp_climate.index.month).mean()
    by_month_maxtemp.index = mean_index

    by_month_mintemp = min_temp_climate.groupby(min_temp_climate.index.month).mean()
    by_month_mintemp.index = mean_index

    graphs1 = Figure(figsize=size, dpi = 100)
    ax1 = graphs1.add_subplot(1,1,1)
    ax1.plot(by_month_meantemp, '-o', label = 'Средняя температура по месяцам', linewidth=1)
    for i_x, i_y in zip(by_month_meantemp.index, by_month_meantemp.iloc[:,0]):
        ax1.text(i_x, i_y, '({})'.format("%.1f" % i_y))
    ax1.plot(by_month_maxtemp, '-o',label = 'Максимальная температура', linewidth=1)
    for i_x, i_y in zip(by_month_maxtemp.index, by_month_maxtemp.iloc[:,0]):
        ax1.text(i_x, i_y, '({})'.format("%.1f" % i_y))
    ax1.plot(by_month_mintemp, '-o', label = 'Минимальная температура', linewidth=1)
    for i_x, i_y in zip(by_month_mintemp.index, by_month_mintemp.iloc[:,0]):
        ax1.text(i_x, i_y, '({})'.format("%.1f" % i_y))
    ax1.minorticks_on()
    ax1.grid(True)
    ax1.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
    ax1.set_title('Температура по месяцам')
    ax1.legend(loc='best', ncol=3)
    add_canvas(graphs1)

    graph_mean_parameter(pressure_climate)
    graph_mean_parameter(wind_climate)
    graph_mean_parameter(precipitation_climate)
    graph_mean_parameter(eff_temp_climate)


def graph_selected_mean_months():
    """Построение графиков средних по месяцам в указанном диапазоне дат"""

    def graph_selected_mean_parameter(parameter):
        parameter = parameter.loc[first_date:second_date]
        by_month_parameter = parameter.groupby(parameter.index.month).mean()
        by_month_parameter.index = mean_index
        graphs = Figure(figsize=size, dpi = 100)
        ax = graphs.add_subplot(1,1,1)
        ax.plot(by_month_parameter, '-o', linewidth=1)
        for i_x, i_y in zip(by_month_parameter.index, by_month_parameter.iloc[:,0]):
            ax.text(i_x, i_y, '({})'.format("%.1f" % i_y))
        ax.minorticks_on()
        ax.grid(True)
        ax.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
        ax.set_title(parameter.columns[0])
        add_canvas(graphs)

    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
        
    climate_months = climate.resample('M').mean()
    
    # Разделение данных климата
    max_temp_climate, min_temp_climate, mean_temp_climate, pressure_climate, wind_climate, precipitation_climate, eff_temp_climate= separate_climate(climate_months)

    first_date = '{}-{}-{}'.format(combobox_start_years.get(), combobox_start_months.get(), combobox_start_days.get())
    second_date = '{}-{}-{}'.format(combobox_finish_years.get(), combobox_finish_months.get(), combobox_finish_days.get())
    mean_index = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']

    try:
        add_fig()
        fig.title('Графики распределения среднемесячных значений климатических параметров в указанном диапазоне дат ({} - {}) "{}"'.format(first_date, second_date, file_name.split('/')[-1]))

        max_temp_climate = max_temp_climate.loc[first_date:second_date]
        min_temp_climate = min_temp_climate.loc[first_date:second_date]
        mean_temp_climate = mean_temp_climate.loc[first_date:second_date]

        by_month_meantemp = mean_temp_climate.groupby(mean_temp_climate.index.month).mean()
        by_month_meantemp.index = mean_index

        by_month_maxtemp = max_temp_climate.groupby(max_temp_climate.index.month).mean()
        by_month_maxtemp.index = mean_index

        by_month_mintemp = min_temp_climate.groupby(min_temp_climate.index.month).mean()
        by_month_mintemp.index = mean_index

        add_frames()

        ttk.Label(second_frame, 
                  text='Графики распределения среднемесячных значений климатических параметров в указанном диапазоне дат ({} - {}) "{}"'.format(first_date, second_date, file_name.split('/')[-1]),
                  font=tkFont.Font(family='Calibri',size=20)).pack()

        graphs1 = Figure(figsize=size, dpi=100)
        ax1 = graphs1.add_subplot(1, 1, 1)
        ax1.plot(by_month_meantemp, '-o', label='Средняя температура по месяцам', linewidth=1)
        for i_x, i_y in zip(by_month_meantemp.index, by_month_meantemp.iloc[:, 0]):
            ax1.text(i_x, i_y, '({})'.format("%.1f" % i_y))
        ax1.plot(by_month_maxtemp, '-o', label='Максимальная температура', linewidth=1)
        for i_x, i_y in zip(by_month_maxtemp.index, by_month_maxtemp.iloc[:,0]):
            ax1.text(i_x, i_y, '({})'.format("%.1f" % i_y))
        ax1.plot(by_month_mintemp, '-o', label='Минимальная температура', linewidth=1)
        for i_x, i_y in zip(by_month_mintemp.index, by_month_mintemp.iloc[:, 0]):
            ax1.text(i_x, i_y, '({})'.format("%.1f" % i_y))
        ax1.minorticks_on()
        ax1.grid(True)
        ax1.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
        ax1.set_title('Температура')
        ax1.legend(loc='best', ncol=3)
        add_canvas(graphs1)

        graph_selected_mean_parameter(pressure_climate)
        graph_selected_mean_parameter(wind_climate)
        graph_selected_mean_parameter(precipitation_climate)
        graph_selected_mean_parameter(eff_temp_climate)       
    except:
        fig.destroy()
        mb.showerror("Ошибка", "Не выбран диапазон дат")
            

def graph_compare_mean_months():
    """Сравнение средних по месяцам в разных диапазонах"""

    def select_first_range():
        global Date_array_first
        
        first_date = '{}-{}-{}'.format(combobox_start_years.get(), combobox_start_months.get(), combobox_start_days.get())
        second_date = '{}-{}-{}'.format(combobox_finish_years.get(), combobox_finish_months.get(), combobox_finish_days.get())
        first_range_label['text'] = 'Первый диапазон: ({}) - ({})'.format(first_date, second_date)
        Date_array_first=[first_date, second_date]
        return Date_array_first

    def select_second_range():
        global Date_array_second
        
        first_date = '{}-{}-{}'.format(combobox_start_years.get(), combobox_start_months.get(), combobox_start_days.get())
        second_date = '{}-{}-{}'.format(combobox_finish_years.get(), combobox_finish_months.get(), combobox_finish_days.get())
        second_range_label['text'] = 'Второй диапазон: ({}) - ({})'.format(first_date, second_date)
        Date_array_second=[first_date, second_date]
        return Date_array_second

    def graph_compare_climate():
        for parameter in result:
            try:
                parameter_first = parameter.loc[Date_array_first[0]:Date_array_first[1]]
                mean_index = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
                by_month_parameter_first = parameter_first.groupby(parameter_first.index.month).mean()
                by_month_parameter_first.index = mean_index

                parameter_second = parameter.loc[Date_array_second[0]:Date_array_second[1]]       
                by_month_parameter_second = parameter_second.groupby(parameter_second.index.month).mean()
                by_month_parameter_second.index = mean_index

                graphs = Figure(figsize=(17, 7), dpi=100)
                ax1 = graphs.add_axes([0.1, 0.1, 0.8, 0.8])
                ax1.plot(by_month_parameter_first, '-o', label = str(Date_array_first[0] + ':' + Date_array_first[1]), alpha=0.5, linewidth=1)
                for i_x, i_y in zip(by_month_parameter_first.index, by_month_parameter_first.iloc[:,0]):
                    ax1.text(i_x, i_y, '({}, {})'.format(str(Date_array_first[0] + ':' + Date_array_first[1]), "%.1f" % i_y))
                ax1.plot(by_month_parameter_second, '-o', label = str(Date_array_second[0] + ':' + Date_array_second[1]), alpha=0.5, linewidth=1)
                for i_x, i_y in zip(by_month_parameter_second.index, by_month_parameter_second.iloc[:,0]):
                    ax1.text(i_x, i_y-2, '({}, {})'.format(str(Date_array_second[0] + ':' + Date_array_second[1]), "%.1f" % i_y))
                ax1.minorticks_on()
                ax1.grid(True)
                ax1.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
                ax1.set_title(f'{parameter.columns[0]} по месяцам')
                graphs.legend(loc='lower center', ncol = 3)

                add_canvas(graphs)       
            except:
                fig.destroy()
                mb.showerror("Ошибка", "Не выбран диапазон дат")

    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
        
    climate_months = climate.resample('M').mean()
    
    # Разделение данных климата
    result = separate_climate(climate_months)

    add_fig()
    fig.title('Сравнение двух диапазонов "{}"'.format(file_name.split('/')[-1]))
    add_frames()
        
    # Выбор дат
    ttk.Label(second_frame, text='Выбор диапазона дат', font=tkFont.Font(family='Calibri',size=18)).pack(side=tk.TOP)

    start_date_frame = ttk.Frame(second_frame)
    start_date_frame.pack(side=tk.TOP)
    combobox_start_days = ttk.Combobox(start_date_frame, textvariable= tk.StringVar(), values=[i for i in range(1,32)])
    combobox_start_days.current(0)
    combobox_start_days.pack(side=tk.LEFT)

    combobox_start_months = ttk.Combobox(start_date_frame, textvariable= tk.StringVar(), values=[i for i in range(1,13)])
    combobox_start_months.current(0)
    combobox_start_months.pack(side=tk.LEFT)

    combobox_start_years = ttk.Combobox(start_date_frame, textvariable= tk.StringVar(), values=[i for i in range(1960,2021)])
    combobox_start_years.current(0)
    combobox_start_years.pack(side=tk.LEFT)

    finish_date_frame = ttk.Frame(second_frame)
    finish_date_frame.pack(side=tk.TOP)
    combobox_finish_days = ttk.Combobox(finish_date_frame, textvariable= tk.StringVar(), values=[i for i in range(1,32)])
    combobox_finish_days.current(30)
    combobox_finish_days.pack(side=tk.LEFT)

    combobox_finish_months = ttk.Combobox(finish_date_frame, textvariable= tk.StringVar(), values=[i for i in range(1,13)])
    combobox_finish_months.current(11)
    combobox_finish_months.pack(side=tk.LEFT)

    combobox_finish_years = ttk.Combobox(finish_date_frame, textvariable= tk.StringVar(), values=[i for i in range(1960,2021)])
    combobox_finish_years.current(60)
    combobox_finish_years.pack(side=tk.LEFT)

    first_date = '{}-{}-{}'.format(combobox_start_years.get(), combobox_start_months.get(), combobox_start_days.get())
    second_date = '{}-{}-{}'.format(combobox_finish_years.get(), combobox_finish_months.get(), combobox_finish_days.get())

    first_range_selection_frame = ttk.Frame(second_frame)
    first_range_selection_frame.pack(side=tk.TOP)
    first_range_label = ttk.Label(first_range_selection_frame, text='Первый диапазон: ({}) - ({})'.format(first_date, second_date), font=tkFont.Font(family='Times',size=12))
    first_range_label.pack(side=tk.LEFT)
    select_first_range_button = ttk.Button(first_range_selection_frame, text = 'Изменить первый диапазон', command = select_first_range)
    select_first_range_button.pack(side=tk.LEFT)
    
    second_range_selection_frame = ttk.Frame(second_frame)
    second_range_selection_frame.pack(side=tk.TOP)
    second_range_label = ttk.Label(second_range_selection_frame, text='Второй диапазон: ({}) - ({})'.format(first_date, second_date), font=tkFont.Font(family='Times',size=12))
    second_range_label.pack(side=tk.LEFT)
    select_second_range_button = ttk.Button(second_range_selection_frame, text = 'Изменить второй диапазон', command = select_second_range)
    select_second_range_button.pack(side=tk.LEFT)
    
    graph_compare_climate_button = ttk.Button(second_frame, text = 'Построить графики', command = graph_compare_climate)
    graph_compare_climate_button.pack(side=tk.TOP)


def filter(parameter):
    """Функция фильтрации климатического параметра. Используется в следующих функциях"""
    global size, combobox_filter, canvas
    max_filter = int(combobox_filter.get())
    function = combobox_function.get()

    label = ttk.Label(canvas, text=f'Количество дней, когда {str(parameter.columns[0]).lower()} {function} {max_filter}', font=tkFont.Font(family='Calibri',size=18))
    canvas.create_window(w, 90, window=label, anchor=tk.N)

    y = 120
    ys = []
    for i in range(1960, 1991):
        filtered_climate = parameter.loc[(parameter.index >= '{}-01-01'.format(i)) &
                                         (parameter.index <= '{}-12-31'.format(i))]
        if function == '<=':
            climateilter = filtered_climate.loc[filtered_climate.iloc[:, 0] <= max_filter]
        elif function == '<':
            climateilter = filtered_climate.loc[filtered_climate.iloc[:, 0] < max_filter]
        elif function == '>':
            climateilter = filtered_climate.loc[filtered_climate.iloc[:, 0] > max_filter]
        elif function == '>=':
            climateilter = filtered_climate.loc[filtered_climate.iloc[:, 0] >= max_filter]
        ys.append(len(climateilter))
        filter_label = ttk.Label(canvas, text='{} г. : {} \n'.format(i, len(climateilter)), font=("Calibri", 12))
        canvas.create_window(w-100, y, window=filter_label, anchor=tk.N)
        y += 20

    y = 120
    for i in range(1991, 2021):
        filtered_climate = parameter.loc[(parameter.index >= '{}-01-01'.format(i)) & (parameter.index <= '{}-12-31'.format(i))]
        if function == '<=':
            climateilter = filtered_climate.loc[filtered_climate.iloc[:, 0] <= max_filter]
        elif function == '<':
            climateilter = filtered_climate.loc[filtered_climate.iloc[:, 0] < max_filter]
        elif function == '>':
            climateilter = filtered_climate.loc[filtered_climate.iloc[:, 0] > max_filter]
        elif function == '>=':
            climateilter = filtered_climate.loc[filtered_climate.iloc[:, 0] >= max_filter]
        ys.append(len(climateilter))
        filter_label = ttk.Label(canvas, text='{} г. : {} \n'.format(i, len(climateilter)), font=("Calibri", 12))
        canvas.create_window(w+100, y, window=filter_label, anchor=tk.N)
        y += 20

    second_frame = tk.Frame(canvas)
    canvas.create_window((w,750),window= second_frame, anchor="n")
    graphs1 = Figure(figsize=(12, 5), dpi = 100)
    ax1 = graphs1.add_subplot(1,1,1)
    xs = [x for x in range(1960,2021)]
    ax1.plot(xs, ys, 'o-', linewidth=1)
    for i_x, i_y in zip(xs, ys):
            ax1.text(i_x, i_y, '{}'.format(i_y))
    ax1.minorticks_on()
    ax1.grid(True)
    ax1.grid(which="minor", ls=':', color='lightgray', linewidth=0.6)
    ax1.set_title(f'Количество дней, когда {str(parameter.columns[0]).lower()} {function} {max_filter}')
    
    filter_canvas = FigureCanvasTkAgg(graphs1, second_frame)  #холст
    filter_canvas.draw()
    filter_canvas.get_tk_widget().pack(side=tk.TOP, expand=True)
    
    toolbar = NavigationToolbar2Tk(filter_canvas, second_frame)  #управление графиками
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.BOTH)

    scrollbar = tk.Scrollbar(canvas, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.place(relx=1, rely=0, relheight=1, anchor=tk.NE)
    canvas.config(yscrollcommand=scrollbar.set, scrollregion=(0, 0, 0, y+600))


def filter_mean_temp():
    """Фильтрация средней температуры"""
    global mean_temp_climate, combobox_filter, combobox_function, canvas    
    
    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
            
    # Разделение данных климата
    max_temp_climate, min_temp_climate, mean_temp_climate, pressure_climate, wind_climate, precipitation_climate, eff_temp_climate = separate_climate(climate)

    add_fig()
    fig.title('Фильтрация средней температуры "{}"'.format(file_name.split('/')[-1]))
    main_frame=tk.Frame(fig)
    main_frame.pack(fill=tk.BOTH, expand=1)
    canvas = tk.Canvas(main_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH,expand=1)

    label_one = ttk.Label(canvas, text='Выберите опорное значение средней температуры и функцию', font=tkFont.Font(family='Calibri',size=18))
    canvas.create_window(w, 0, window=label_one, anchor=tk.N)
    
    combobox_filter = ttk.Combobox(main_frame, textvariable= tk.StringVar(), values=[i for i in range(-50,51)])
    combobox_filter.current(40)
    canvas.create_window(w+100, 30, window=combobox_filter, anchor=tk.N)

    combobox_function = ttk.Combobox(main_frame, textvariable= tk.StringVar(), values=['<', '<=', '>', '>='])
    combobox_function.current(1)
    canvas.create_window(w-100, 30, window=combobox_function, anchor=tk.N)

    button_filter = ttk.Button(main_frame, text='Отфильтровать', command=lambda: filter(mean_temp_climate))
    canvas.create_window(w, 60, window=button_filter, anchor=tk.N)
        

def filter_max_temp():
    """Фильтрация максимальной температуры"""
    global max_temp_climate, combobox_filter, combobox_function, canvas     
    
    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
            
    # Разделение данных климата
    max_temp_climate, min_temp_climate, mean_temp_climate, pressure_climate, wind_climate, precipitation_climate, eff_temp_climate = separate_climate(climate)

    add_fig()
    fig.title('Фильтрация максимальной температуры "{}"'.format(file_name.split('/')[-1]))
    main_frame=tk.Frame(fig)
    main_frame.pack(fill=tk.BOTH, expand=1)
    canvas = tk.Canvas(main_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH,expand=1)

    label_one = ttk.Label(canvas, text='Выберите опорное значение максимальной температуры и функцию', font=tkFont.Font(family='Calibri',size=18))
    canvas.create_window(w, 0, window=label_one, anchor=tk.N)
    
    combobox_filter = ttk.Combobox(main_frame, textvariable= tk.StringVar(), values=[i for i in range(-50,51)])
    combobox_filter.current(40)
    canvas.create_window(w+100, 30, window=combobox_filter, anchor=tk.N)

    combobox_function = ttk.Combobox(main_frame, textvariable= tk.StringVar(), values=['<', '<=', '>', '>='])
    combobox_function.current(1)
    canvas.create_window(w-100, 30, window=combobox_function, anchor=tk.N)

    button_filter = ttk.Button(main_frame, text='Отфильтровать', command=lambda: filter(max_temp_climate))
    canvas.create_window(w, 60, window=button_filter, anchor=tk.N)


def filter_min_temp():
    """Фильтрация минимальной температуры"""
    global min_temp_climate, combobox_filter, combobox_function, canvas    
           
    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
            
    # Разделение данных климата
    max_temp_climate, min_temp_climate, mean_temp_climate, pressure_climate, wind_climate, precipitation_climate, eff_temp_climate = separate_climate(climate)

    add_fig()
    fig.title('Фильтрация минимальной температуры "{}"'.format(file_name.split('/')[-1]))
    main_frame=tk.Frame(fig)
    main_frame.pack(fill=tk.BOTH, expand=1)
    canvas = tk.Canvas(main_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH,expand=1)

    label_one = ttk.Label(canvas, text='Выберите опорное значение минимальной температуры и функцию', font=tkFont.Font(family='Calibri',size=18))
    canvas.create_window(w, 0, window=label_one, anchor=tk.N)
    
    combobox_filter = ttk.Combobox(main_frame, textvariable= tk.StringVar(), values=[i for i in range(-50,51)])
    combobox_filter.current(40)
    canvas.create_window(w+100, 30, window=combobox_filter, anchor=tk.N)

    combobox_function = ttk.Combobox(main_frame, textvariable= tk.StringVar(), values=['<', '<=', '>', '>='])
    combobox_function.current(1)
    canvas.create_window(w-100, 30, window=combobox_function, anchor=tk.N)

    button_filter = ttk.Button(main_frame, text='Отфильтровать', command=lambda: filter(min_temp_climate))
    canvas.create_window(w, 60, window=button_filter, anchor=tk.N)


def filter_pressure():
    """Фильтрация атмосферного давления"""
    global pressure_climate, combobox_filter, combobox_function, canvas    
       
    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
    
    # Разделение данных климата
    max_temp_climate, min_temp_climate, mean_temp_climate, pressure_climate, wind_climate, precipitation_climate, eff_temp_climate= separate_climate(climate)
        
    add_fig()
    fig.title('Фильтрация атмосферного давления "{}"'.format(file_name.split('/')[-1]))
    
    main_frame=tk.Frame(fig)
    main_frame.pack(fill=tk.BOTH, expand=1)
    canvas = tk.Canvas(main_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH,expand=1)

    label_one = ttk.Label(canvas, text='Выберите опорное значение атмосферного давления и функцию для сравнения', font=tkFont.Font(family='Calibri',size=18))
    canvas.create_window(w, 0, window=label_one, anchor=tk.N)
    
    combobox_filter = ttk.Combobox(main_frame, textvariable= tk.StringVar(), values=[i for i in range(800,1201)])
    combobox_filter.current(200)
    canvas.create_window(w+100, 30, window=combobox_filter, anchor=tk.N)

    combobox_function = ttk.Combobox(main_frame, textvariable= tk.StringVar(), values=['<', '<=', '>', '>='])
    combobox_function.current(1)
    canvas.create_window(w-100, 30, window=combobox_function, anchor=tk.N)

    button_filter = ttk.Button(main_frame, text='Отфильтровать', command=lambda: filter(pressure_climate))
    canvas.create_window(w, 60, window=button_filter, anchor=tk.N)


def filter_precipitation():
    """Фильтрация количества осадков"""
    global precipitation_climate, combobox_filter, combobox_function, canvas    
    
    if file_name == '':
        mb.showerror("Ошибка", "Не выбран файл для обработки")
        return
    
    # Разделение данных климата
    max_temp_climate, min_temp_climate, mean_temp_climate, pressure_climate, wind_climate, precipitation_climate, eff_temp_climate= separate_climate(climate)
        
    add_fig()
    fig.title('Фильтрация количества осадков "{}"'.format(file_name.split('/')[-1]))
    
    main_frame=tk.Frame(fig)
    main_frame.pack(fill=tk.BOTH, expand=1)
    canvas = tk.Canvas(main_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH,expand=1)

    label_one = ttk.Label(canvas, text='Выберите опорное значение количества осадков и функцию для сравнения', font=tkFont.Font(family='Calibri',size=18))
    canvas.create_window(w, 0, window=label_one, anchor=tk.N)
    
    combobox_filter = ttk.Combobox(main_frame, textvariable= tk.StringVar(), values=[i for i in range(0,300)])
    combobox_filter.current(20)
    canvas.create_window(w+100, 30, window=combobox_filter, anchor=tk.N)

    combobox_function = ttk.Combobox(main_frame, textvariable= tk.StringVar(), values=['<', '<=', '>', '>='])
    combobox_function.current(1)
    canvas.create_window(w-100, 30, window=combobox_function, anchor=tk.N)

    button_filter = ttk.Button(main_frame, text='Отфильтровать', command=lambda: filter(precipitation_climate))
    canvas.create_window(w, 60, window=button_filter, anchor=tk.N)


def wind_rose():
    """Построение розы ветров"""

    def find_coordinates(city_name):
        if city_name in cities["Name"].values:
            series = cities.loc[cities['Name'] == city_name] #поиск строк данных для городов имя которых равно аргументу функции city_name
            one_city = series[:1] #выбор первой строки с таким названием (если их несколько)
            str_coordinates = one_city["Coordinates"].values[0] #получение значения координат в виде строки
            list_coordinates = str_coordinates.split(", ") #разбиение координат на широту и долготу
            latitude = float(list_coordinates[0]) #преобразование строкового значения широты в число
            longitude = float(list_coordinates[1]) #преобразование строкового значения долготы в число
            result = Point(latitude, longitude) #возврат точки на карте
        else:
            result = 0
        return result
    

    def to_date(date):
        format = "%d.%m.%Y"
        datetime_str = datetime.strptime(date, format)
        return datetime_str
    

    def get_daily_meteo(city, start, end):
        location = find_coordinates(city)
        period_start = to_date(start)
        period_end = to_date(end)
        meteo = Daily(location, period_start, period_end)
        result = meteo.fetch()
        return result


    def make_wind_rose():
        try:
            city = get_daily_meteo(city_entry.get(), '{}.{}.{}'.format(combobox_start_days.get(), combobox_start_months.get(), combobox_start_years.get()),
                            '{}.{}.{}'.format(combobox_finish_days.get(), combobox_finish_months.get(), combobox_finish_years.get()))
            graphs = Figure(figsize=(8,6),dpi=100)
            ws = city["wspd"]
            wd = city["wdir"]
            ax = WindroseAxes.from_ax(fig = graphs)
            ax.bar(wd, ws, normed=True, opening=0.8, edgecolor='white')
            ax.set_title('Роза ветров {}'.format(city_entry.get()))
            ax.set_legend(loc='best')

            add_canvas(graphs)
                
        except:
            mb.showinfo(title="Внимание", message="Этот город отсутствует в базе данных")
                
        
    cities = pd.read_excel("russian_cities.xlsx")
    
    add_fig()
    fig.title('Построение розы ветров')
    
    add_frames()
   
    ttk.Label(second_frame, text='Введите город на английском языке (например Moscow)', font=tkFont.Font(family='Calibri',size=18)).pack(side=tk.TOP)
        
    city_entry = ttk.Entry(second_frame)
    city_entry.pack(side=tk.TOP)

    ttk.Label(second_frame, text='Выбор диапазона дат', font=tkFont.Font(family='Calibri',size=18)).pack(side=tk.TOP)  
    
    start_date_frame = ttk.Frame(second_frame)
    start_date_frame.pack(side=tk.TOP)
    combobox_start_days = ttk.Combobox(start_date_frame, textvariable= tk.StringVar(), values=[i for i in range(1,32)])
    combobox_start_days.current(0)
    combobox_start_days.pack(side=tk.LEFT)

    combobox_start_months = ttk.Combobox(start_date_frame, textvariable= tk.StringVar(), values=[i for i in range(1,13)])
    combobox_start_months.current(0)
    combobox_start_months.pack(side=tk.LEFT)

    combobox_start_years = ttk.Combobox(start_date_frame, textvariable= tk.StringVar(), values=[i for i in range(1960,2021)])
    combobox_start_years.current(0)
    combobox_start_years.pack(side=tk.LEFT)

    finish_date_frame = ttk.Frame(second_frame)
    finish_date_frame.pack(side=tk.TOP)
    combobox_finish_days = ttk.Combobox(finish_date_frame, textvariable= tk.StringVar(), values=[i for i in range(1,32)])
    combobox_finish_days.current(30)
    combobox_finish_days.pack(side=tk.LEFT)

    combobox_finish_months = ttk.Combobox(finish_date_frame, textvariable= tk.StringVar(), values=[i for i in range(1,13)])
    combobox_finish_months.current(11)
    combobox_finish_months.pack(side=tk.LEFT)

    combobox_finish_years = ttk.Combobox(finish_date_frame, textvariable= tk.StringVar(), values=[i for i in range(1960,2021)])
    combobox_finish_years.current(60)
    combobox_finish_years.pack(side=tk.LEFT)

    ttk.Button(second_frame, text = 'Построить розу ветров', command=make_wind_rose).pack(side=tk.TOP)
  

def main():
    """Основная функция"""
    global file_name, size, file_chosen_label, w, h, combobox_start_days, combobox_start_months, combobox_start_years, combobox_finish_days, combobox_finish_months, combobox_finish_years
    file_name = ''  #Переменная с названием файла для обработки
    size = (18,8)  #Размер графиков

    # Окно приложения
    root = tk.Tk()
    root.title('Анализ специализированных климатических характеристик')

    w = root.winfo_screenwidth() // 3
    h = root.winfo_screenheight() - 70
    root.geometry('{}x{}+0+0'.format(w, h))
    root.wm_iconbitmap('climate.ico')

    # Рамка для виджетов
    frame = tk.Frame(root, padx= 50, pady = 50)
    frame.pack(expand=True)

    # Кнопка выбора файла
    import_xlsx_file_button = ttk.Button(frame, text = 'Выбрать файл', command = import_file)
    import_xlsx_file_button.grid(row = 0, column=0, columnspan=3)

    # Метка выбора файла
    file_chosen_label = ttk.Label(frame, text='Файл не выбран', foreground='red', font=tkFont.Font(family='Calibri',size=12))
    file_chosen_label.grid(row=1, column=0, columnspan=3)

    # Кнопка таблицы данных
    table_button = ttk.Button(frame, text = 'Таблица данных', command = table_climate)
    table_button.grid(row = 2, column= 0, columnspan=3)

    # Кнопка мат статистики
    math_button = ttk.Button(frame, text = 'Статистические характеристики', command = raschet)
    math_button.grid(row = 3, column= 0, columnspan=3)

    # Кнопка пострения графиков
    graph_button = ttk.Button(frame, text = 'Построить графики распределения', command = graph_climate)
    graph_button.grid(row = 4, column= 0, columnspan=3)

    # Кнопка годичных графиков
    graph_year_button = ttk.Button(frame, text = 'Построить графики среднегодовых значений', command = graph_year_climate)
    graph_year_button.grid(row = 5, column= 0, columnspan=3)

    # Кнопка месячных графиков
    graph_month_button = ttk.Button(frame, text = 'Построить графики среднемесячных значений', command = graph_month_climate)
    graph_month_button.grid(row = 6, column= 0, columnspan=3)

    # Кнопка построения гистограмм
    histo_button = ttk.Button(frame, text = 'Построить гистограммы плотности распределения', command = histo_climate)
    histo_button.grid(row = 7, column= 0, columnspan=3)

    # Кнопка построения kde
    graph_year_button = ttk.Button(frame, text = 'Построить графики плотности распределения', command = kde_climate)
    graph_year_button.grid(row = 8, column= 0, columnspan=3)

    # Кнопка среднего по месяцам
    graph_mean_month_button = ttk.Button(frame, text = 'Построить графики средних по месяцам', command = graph_mean_months)
    graph_mean_month_button.grid(row = 9, column= 0, columnspan=3)

    # Кнопка вывода 2 диапазонов
    graph_compare_mean_month_button = ttk.Button(frame, text = 'Сравнение средних по месяцам в двух диапазонах', command = graph_compare_mean_months)
    graph_compare_mean_month_button.grid(row = 10, column= 0, columnspan=3)

    # Кнопка фильтра средней температуры
    filter_mean_temp_button = ttk.Button(frame, text = 'Фильтр средней температуры', command = filter_mean_temp)
    filter_mean_temp_button.grid(row = 11, column= 0, columnspan=3)

    # Кнопка фильтра максимальной температуры
    filter_max_temp_button = ttk.Button(frame, text = 'Фильтр максимальной температуры', command = filter_max_temp)
    filter_max_temp_button.grid(row = 12, column= 0, columnspan=3)

    # Кнопка фильтра минимальной температуры
    filter_min_temp_button = ttk.Button(frame, text = 'Фильтр минимальной температуры', command = filter_min_temp)
    filter_min_temp_button.grid(row = 13, column= 0, columnspan=3)

    # Кнопка фильтра атмосферного давления
    filter_pressure_button = ttk.Button(frame, text = 'Фильтр атмосферного давления', command = filter_pressure)
    filter_pressure_button.grid(row = 14, column= 0, columnspan=3)

    # Кнопка фильтра атмосферного давления
    filter_precipitation_button = ttk.Button(frame, text = 'Фильтр количества осадков', command = filter_precipitation)
    filter_precipitation_button.grid(row = 15, column= 0, columnspan=3)

    # Кнопка wind_rose
    wind_rose_button = ttk.Button(frame, text = 'Построить розу ветров', command = wind_rose)
    wind_rose_button.grid(row = 16, column= 0, columnspan=3)

    # Выбор дат
    label = ttk.Label(frame, text='Выбор диапазона дат', font=tkFont.Font(family='Calibri',size=18))
    label.grid(row=17, column=0, columnspan=3)

    label_days = ttk.Label(frame, text='День', font=tkFont.Font(family='Calibri',size=14))
    label_days.grid(row=18, column=0)

    label_months = ttk.Label(frame, text='Месяц', font=tkFont.Font(family='Calibri',size=14))
    label_months.grid(row=18, column=1)

    label_years = ttk.Label(frame, text='Год', font=tkFont.Font(family='Calibri',size=14))
    label_years.grid(row=18, column=2)

    combobox_start_days = ttk.Combobox(frame, textvariable= tk.StringVar(), values=[i for i in range(1,32)])
    combobox_start_days.current(0)
    combobox_start_days.grid(row=19, column=0)

    combobox_start_months = ttk.Combobox(frame, textvariable= tk.StringVar(), values=[i for i in range(1,13)])
    combobox_start_months.current(0)
    combobox_start_months.grid(row=19, column=1)

    combobox_start_years = ttk.Combobox(frame, textvariable= tk.StringVar(), values=[i for i in range(1960,2021)])
    combobox_start_years.current(0)
    combobox_start_years.grid(row=19, column=2)

    combobox_finish_days = ttk.Combobox(frame, textvariable= tk.StringVar(), values=[i for i in range(1,32)])
    combobox_finish_days.current(30)
    combobox_finish_days.grid(row=20, column=0)

    combobox_finish_months = ttk.Combobox(frame, textvariable= tk.StringVar(), values=[i for i in range(1,13)])
    combobox_finish_months.current(11)
    combobox_finish_months.grid(row=20, column=1)

    combobox_finish_years = ttk.Combobox(frame, textvariable= tk.StringVar(), values=[i for i in range(1960,2021)])
    combobox_finish_years.current(60)
    combobox_finish_years.grid(row=20, column=2)

    # Кнопка мат статистики в диапазоне
    selected_math_button = ttk.Button(frame, text = 'Статистические характеристики в указанном диапазоне', command = selected_raschet)
    selected_math_button.grid(row = 21, column= 0, columnspan=3)

    # Кнопка построения графика в диапазоне
    select_graph_button = ttk.Button(frame, text = 'Построить графики в указанном диапазоне дат', command= graph_selected_climate)
    select_graph_button.grid(row = 22, column=0,columnspan=3)

    # Кнопка месячных графиков в указанном диапазоне
    graph_selected_month_climate_button = ttk.Button(frame, text = 'Построить графики среднемесячных значений в указанном диапазоне дат', command = graph_selected_month_climate)
    graph_selected_month_climate_button.grid(row = 23, column= 0, columnspan=3)
    
    # Кнопка построения гистограмм в диапазоне
    histo_button = ttk.Button(frame, text = 'Построить гистограммы плотности распределения в указанном диапазоне', command = histo_selected_climate)
    histo_button.grid(row = 24, column= 0, columnspan=3)

    # Кнопка построения графиков плотности распределения в диапазоне
    kde_selected_button = ttk.Button(frame, text = 'Построить графики плотности распределения в указанном диапазоне', command = kde_selected_climate)
    kde_selected_button.grid(row = 25, column= 0, columnspan=3)
    
    # Кнопка среднего по месяцам в указанном диапазоне
    graph_selected_mean_month_button = ttk.Button(frame, text='Построить графики средних по месяцам в указанном диапазоне', command = graph_selected_mean_months)
    graph_selected_mean_month_button.grid(row=26, column=0, columnspan=3)

    tk.mainloop()


if __name__ == "__main__":
    main()
