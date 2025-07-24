# -*- coding: utf-8 -*-
"""
Created on Sat May 31 22:16:57 2025

@author: Влад
"""

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import configparser

from library.common import fill_treeview, refresh_tree, save_csv, save_excel, save_pickle, save_png


#Загрузка параметров конфигурационного файла
def load_config():
    """
    

    Returns
    -------
    dict
        DESCRIPTION.

    """
    config = configparser.ConfigParser()
    config.read("C:/work/scripts/settings.ini")
    return {
        "bg_color": config.get("UI", "bg_color", fallback="#ffffff"),
        "font_family": config.get("UI", "font_family", fallback="Arial"),
        "font_size": config.getint("UI", "font_size", fallback=12)
    }

config = load_config()

#Загрузка данных из баз
os.chdir("C:/work")
cashiers = pd.read_pickle("C:/work/data/cashiers.pick")
client_type = pd.read_pickle("C:/work/data/client_type.pick")
menu = pd.read_pickle("C:/work/data/menu.pick")
order = pd.read_pickle("C:/work/data/order.pick")
orders = pd.read_pickle("C:/work/data/orders.pick")



#Обновление данных справочников
def reload_data():
    """
    

    Returns
    -------
    None.

    """
    global cashiers, client_type, menu, order, orders
    cashiers = pd.read_pickle("C:/work/data/cashiers.pick")
    client_type = pd.read_pickle("C:/work/data/client_type.pick")
    menu = pd.read_pickle("C:/work/data/menu.pick")
    order = pd.read_pickle("C:/work/data/order.pick")
    orders = pd.read_pickle("C:/work/data/orders.pick")



#Добавление новой строки в базу данных
def add_database_row(database, tree):
    """
    

    Parameters
    ----------
    database : TYPE
        DESCRIPTION.
    tree : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    next_id = database[database.columns[0]].max() + 1 if not database.empty else 1
    types = list(map(type, database.iloc[0]))

    def types_first(t):
        """
        

        Parameters
        ----------
        t : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        if t == pd.Timestamp:
            return pd.Timestamp.now()
        try:
            return t()
        except TypeError:
            return None

    if types[0] == pd.Timestamp:
        database.loc[len(database)] = [pd.Timestamp.now()] + [types_first(t) for t in types[1:]]
    else:
        database.loc[len(database)] = [next_id] + [types_first(t) for t in types[1:]]
    refresh_tree(tree, database)

#Удаление строки из базы данных
def delete_database_row(database, tree):
    """
    

    Parameters
    ----------
    database : TYPE
        DESCRIPTION.
    tree : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    selected_item = tree.selection()[0]
    if not selected_item:
        return
    database.drop(index=int(selected_item), inplace=True)
    database.reset_index(drop=True, inplace=True)
    refresh_tree(tree, database)

#Редактирование данных справочника
def edit_by_click(event, tree, database, new_window):
    """
    

    Parameters
    ----------
    event : TYPE
        DESCRIPTION.
    tree : TYPE
        DESCRIPTION.
    database : TYPE
        DESCRIPTION.
    new_window : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    #Защита окна от создания двойного виджета ввода
    if hasattr(tree, 'active_entry') and tree.active_entry is not None:
        return

    #Редактирование ячейки с защитой от реадктирования первой колонки
    selection = tree.selection()
    if not selection:
        return
    item = selection[0]

    col = tree.identify_column(event.x)
    col_idx = int(col[1:]) - 1

    if col_idx == 0 and not database.equals(order):
        return
        
    # Получаем координаты ячейки относительно дерева
    x, y, width, height = tree.bbox(item, col)

    # Преобразуем координаты в абсолютные в пределах окна
    abs_x = tree.winfo_rootx() + x - new_window.winfo_rootx()
    abs_y = tree.winfo_rooty() + y - new_window.winfo_rooty()

    entry = ttk.Entry(new_window)
    tree.active_entry = entry
    entry.insert(0, tree.item(item, "values")[col_idx])
    entry.place(x=abs_x, y=abs_y, width=width, height=height)


    #Обновление таблицы с учетом новых данных  
    def save_edit():
        """
        

        Returns
        -------
        None.

        """
        row_idx = int(item)
        try:
            value = type(database.iloc[row_idx, col_idx])(entry.get())
        except Exception:
            value = entry.get()
        database.iloc[row_idx, col_idx] = value
        refresh_tree(tree, database)
        entry.destroy()
        tree.active_entry = None
        
    entry.bind("<Return>", lambda e: save_edit())
    entry.bind("<FocusOut>", lambda e: save_edit())
    


#Создание окон редактирования баз данных (название_database)
def cashiers_database(root):
    """
    

    Parameters
    ----------
    root : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    new_window = tk.Toplevel(root)
    new_window.configure(bg=config["bg_color"])

    #Создаем заголовок
    label = tk.Label(new_window, text="Кассиры", font=(config["font_family"], config["font_size"], "bold"), bg=config["bg_color"])
    label.pack(pady=10)

    current_df = cashiers

    #Создание таблицы
    tree = ttk.Treeview(new_window, columns=list(current_df.columns), show="headings")
    fill_treeview(new_window, current_df, tree)
    tree.pack(expand=True, fill="both")

    tree.bind("<Double-1>", lambda e: edit_by_click(e, tree, current_df, new_window))

    #Создаем группу кнопок
    frame = tk.Frame(new_window, bg=config["bg_color"])
    frame.pack(padx=110, pady=5, anchor="nw")

    #Создаем кнопку добавления
    button = tk.Button(frame, 
                   text="Добавить", 
                   command=lambda: add_database_row(current_df, tree))
    button.pack(side="left", padx=5, pady=5, anchor="n")

    #Создаем кнопку удаления
    btn = tk.Button(frame, text="Удалить", command=lambda: delete_database_row(current_df, tree))
    btn.pack(side="left", padx=5, pady=5, anchor="n")

    #Создаем кнопку сохранения в pickle
    btn = tk.Button(frame, text="Сохранить", command=lambda: save_pickle(current_df, "cashiers"))
    btn.pack(side="left", padx=5, pady=5, anchor="n")

    #Создаем кнопку сохранения в Excel
    btn = tk.Button(frame, text="Экспорт в Excel", command=lambda: save_excel(current_df, "cashiers"))
    btn.pack(side="left", padx=5, pady=5, anchor="n")


def client_types_database(root):
    """
    

    Parameters
    ----------
    root : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    new_window = tk.Toplevel(root)
    new_window.configure(bg=config["bg_color"])

    #Создаем заголовок
    label = tk.Label(new_window, text="Типы клиентов", font=(config["font_family"], config["font_size"], "bold"), bg=config["bg_color"])
    label.pack(pady=10)

    current_df = client_type

    #Создание таблицы
    tree = ttk.Treeview(new_window, columns=list(current_df.columns), show="headings")
    fill_treeview(new_window, current_df, tree)
    tree.pack(expand=True, fill="both")

    tree.bind("<Double-1>", lambda e: edit_by_click(e, tree, current_df, new_window))

    #Создаем группу кнопок
    frame = tk.Frame(new_window, bg=config["bg_color"])
    frame.pack(padx=110, pady=5, anchor="nw")

    #Создаем кнопку добавления
    button = tk.Button(frame, 
                   text="Добавить", 
                   command=lambda: add_database_row(current_df, tree))
    button.pack(side="left", padx=5, pady=5, anchor="n")

    #Создаем кнопку удаления
    btn = tk.Button(frame, text="Удалить", command=lambda: delete_database_row(current_df, tree))
    btn.pack(side="left", padx=5, pady=5, anchor="n")

    #Создаем кнопку сохранения в pickle
    btn = tk.Button(frame, text="Сохранить", command=lambda: save_pickle(current_df, "client_type"))
    btn.pack(side="left", padx=5, pady=5, anchor="n")

    #Создаем кнопку сохранения в Excel
    btn = tk.Button(frame, text="Экспорт в Excel", command=lambda: save_excel(current_df, "client_types"))
    btn.pack(side="left", padx=5, pady=5, anchor="n")

def menu_database(root):
    """
    

    Parameters
    ----------
    root : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    new_window = tk.Toplevel(root)
    new_window.configure(bg=config["bg_color"])

    #Создаем заголовок
    label = tk.Label(new_window, text="Меню", font=(config["font_family"], config["font_size"], "bold"), bg=config["bg_color"])
    label.pack(pady=10)

    current_df = menu

    #Создание таблицы
    tree = ttk.Treeview(new_window, columns=list(current_df.columns), show="headings")
    fill_treeview(new_window, current_df, tree)
    tree.pack(expand=True, fill="both")

    tree.bind("<Double-1>", lambda e: edit_by_click(e, tree, current_df, new_window))

    #Создаем группу кнопок
    frame = tk.Frame(new_window, bg=config["bg_color"])
    frame.pack(padx=110, pady=5, anchor="nw")

    #Создаем кнопку добавления
    button = tk.Button(frame, 
                   text="Добавить", 
                   command=lambda: add_database_row(current_df, tree))
    button.pack(side="left", padx=5, pady=5, anchor="n")

    #Создаем кнопку удаления
    btn = tk.Button(frame, text="Удалить", command=lambda: delete_database_row(current_df, tree))
    btn.pack(side="left", padx=5, pady=5, anchor="n")

    #Создаем кнопку сохранения в pickle
    btn = tk.Button(frame, text="Сохранить", command=lambda: save_pickle(current_df, "menu"))
    btn.pack(side="left", padx=5, pady=5, anchor="n")

    #Создаем кнопку сохранения в Excel
    btn = tk.Button(frame, text="Экспорт в Excel", command=lambda: save_excel(current_df, "menu"))
    btn.pack(side="left", padx=5, pady=5, anchor="n")

def order_database(root):
    """
    

    Parameters
    ----------
    root : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    new_window = tk.Toplevel(root)
    new_window.configure(bg=config["bg_color"])

    #Создаем заголовок
    label = tk.Label(new_window, text="Состав заказов", font=(config["font_family"], config["font_size"], "bold"), bg=config["bg_color"])
    label.pack(pady=10)

    current_df = order

    #Создание таблицы
    tree = ttk.Treeview(new_window, columns=list(current_df.columns), show="headings")
    fill_treeview(new_window, current_df, tree)
    tree.pack(expand=True, fill="both")

    tree.bind("<Double-1>", lambda e: edit_by_click(e, tree, current_df, new_window))

    #Создаем группу кнопок
    frame = tk.Frame(new_window, bg=config["bg_color"])
    frame.pack(padx=110, pady=5, anchor="nw")

    #Создаем кнопку добавления
    button = tk.Button(frame, 
                   text="Добавить", 
                   command=lambda: add_database_row(current_df, tree))
    button.pack(side="left", padx=5, pady=5, anchor="n")

    #Создаем кнопку удаления
    btn = tk.Button(frame, text="Удалить", command=lambda: delete_database_row(current_df, tree))
    btn.pack(side="left", padx=5, pady=5, anchor="n")

    #Создаем кнопку сохранения в pickle
    btn = tk.Button(frame, text="Сохранить", command=lambda: save_pickle(current_df, "order"))
    btn.pack(side="left", padx=5, pady=5, anchor="n")

    #Создаем кнопку сохранения в Excel
    btn = tk.Button(frame, text="Экспорт в Excel", command=lambda: save_excel(current_df, "order"))
    btn.pack(side="left", padx=5, pady=5, anchor="n")

def orders_database(root):
    """
    

    Parameters
    ----------
    root : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    new_window = tk.Toplevel(root)
    new_window.configure(bg=config["bg_color"])

    #Создаем заголовок
    label = tk.Label(new_window, text="Заказы", font=(config["font_family"], config["font_size"], "bold"), bg=config["bg_color"])
    label.pack(pady=10)

    current_df = orders

    #Создание таблицы
    tree = ttk.Treeview(new_window, columns=list(current_df.columns), show="headings")
    fill_treeview(new_window, current_df, tree)
    tree.pack(expand=True, fill="both")

    tree.bind("<Double-1>", lambda e: edit_by_click(e, tree, current_df, new_window))

    #Создаем группу кнопок
    frame = tk.Frame(new_window, bg=config["bg_color"])
    frame.pack(padx=110, pady=5, anchor="nw")

    #Создаем кнопку добавления
    button = tk.Button(frame, 
                   text="Добавить", 
                   command=lambda: add_database_row(current_df, tree))
    button.pack(side="left", padx=5, pady=5, anchor="n")

    #Создаем кнопку удаления
    btn = tk.Button(frame, text="Удалить", command=lambda: delete_database_row(current_df, tree))
    btn.pack(side="left", padx=5, pady=5, anchor="n")

    #Создаем кнопку сохранения в pickle
    btn = tk.Button(frame, text="Сохранить", command=lambda: save_pickle(current_df, "orders"))
    btn.pack(side="left", padx=5, pady=5, anchor="n")

    #Создаем кнопку сохранения в Excel
    btn = tk.Button(frame, text="Экспорт в Excel", command=lambda: save_excel(current_df, "orders"))
    btn.pack(side="left", padx=5, pady=5, anchor="n")

def type_of_pay(root):
    """
    

    Parameters
    ----------
    root : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    #Прикручиваем график и кнопку
    new_window = tk.Toplevel(root)
    new_window.configure(bg=config["bg_color"])

    #Создаем заголовок
    label = tk.Label(new_window, text="Тип оплаты по категориям клиентов", font=(config["font_family"], config["font_size"], "bold"), bg=config["bg_color"])
    label.pack(pady=10)
    
    #Заимствуем логику из прошлого дз
    fig, ax = plt.subplots(figsize=(12, 6))
    mg_1 = orders.merge(client_type, left_on="тип клиента", right_on="type_id", how="inner")
    sns.countplot(data=mg_1, x="тип", hue="тип оплаты ")
    plt.title("Типы оплаты по категориям клиентов")

    #Создаем группу кнопок
    frame = tk.Frame(new_window, bg=config["bg_color"])
    frame.pack(anchor="n")
    
    #Создаем кнопку обновления
    button = tk.Button(frame, 
                   text="Обновить", 
                   command=lambda: upd_type_of_pay(ax, canvas))
    button.pack(side="left", padx=5, pady=5, anchor="n")

    #Создаем кнопку сохранения в png
    btn = tk.Button(frame, text="Экспорт в png", command=lambda: save_png(fig, "type_of_pay"))
    btn.pack(side="left", padx=5, pady=5, anchor="n")

    
    #Встраиваем график в ткинтер окно
    canvas = FigureCanvasTkAgg(fig, master=new_window)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)
    
    #ссылки
    new_window.fig = fig
    new_window.ax = ax
    new_window.canvas = canvas
    
def orders_by_hour(root):
    """
    

    Parameters
    ----------
    root : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    #Также прикручиваем график и кнопку
    new_window = tk.Toplevel(root)
    new_window.configure(bg=config["bg_color"])
    
    #Создаем заголовок
    label = tk.Label(new_window, text="Распределение заказов по часам", font=(config["font_family"], config["font_size"], "bold"), bg=config["bg_color"])
    label.pack(pady=10)
    
    #Заимствуем логику из прошлого дз
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.histplot(data=orders, x="дата_время", bins=20, kde=True, color="purple")
    plt.title("Распределение заказов по часам")

    #Создаем группу кнопок
    frame = tk.Frame(new_window, bg=config["bg_color"])
    frame.pack(anchor="n")

    #Создаем кнопку обновления
    button = tk.Button(frame, 
                   text="Обновить", 
                   command=lambda: upd_orders_by_hour(ax, canvas))
    button.pack(side="left", pady=5, padx=5)

    #Создаем кнопку сохранения в png
    btn = tk.Button(frame, text="Экспорт в png", command=lambda: save_png(fig, "orders_by_hour"))
    btn.pack(side="left", padx=5, pady=5)
    
    #Встраиваем график в ткинтер окно
    canvas = FigureCanvasTkAgg(fig, master=new_window)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)
    
    #ссылки
    new_window.fig = fig
    new_window.ax = ax
    new_window.canvas = canvas

def price_boxplot(root):
    """
    

    Parameters
    ----------
    root : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    #Также прикручиваем график и кнопку
    new_window = tk.Toplevel(root)
    new_window.configure(bg=config["bg_color"])
    
    #Создаем заголовок
    label = tk.Label(new_window, text="Разброс цен по категориям блюд", font=(config["font_family"], config["font_size"], "bold"), bg=config["bg_color"])
    label.pack(pady=10)
    
    #Заимствуем логику из прошлого дз
    fig, ax = plt.subplots(figsize=(16, 6))
    sns.boxplot(data=menu, y="цена", x="категория")
    plt.title("Разброс цен по категориям блюд")

    #Создаем группу кнопок
    frame = tk.Frame(new_window, bg=config["bg_color"])
    frame.pack(anchor="n")

    #Создаем кнопку
    button = tk.Button(frame, 
                   text="Обновить", 
                   command=lambda: upd_price_boxplot(ax, canvas))
    button.pack(side="left", padx=5, pady=5)

    #Создаем кнопку сохранения в png
    btn = tk.Button(frame, text="Экспорт в png", command=lambda: save_png(fig, "price_boxplot"))
    btn.pack(side="left", padx=5, pady=5)
    
    #Встраиваем график в ткинтер окно
    canvas = FigureCanvasTkAgg(fig, master=new_window)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)
    
    #ссылки
    new_window.fig = fig
    new_window.ax = ax
    new_window.canvas = canvas

def sum_scatter(root):
    """
    

    Parameters
    ----------
    root : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    #Также прикручиваем график и кнопку
    new_window = tk.Toplevel(root)
    new_window.configure(bg=config["bg_color"])
    
    #Создаем заголовок
    label = tk.Label(new_window, text="Распределение суммы заказа по времени и типам клиентов", font=(config["font_family"], config["font_size"], "bold"), bg=config["bg_color"])
    label.pack(pady=10)
    
    #Заимствуем логику из прошлого дз
    order_sum = order.merge(menu, left_on="позиция", right_on="dish_id", how="inner")
    order_sum["сумма позиции"] = order_sum["количество"] * order_sum["цена"]
    order_totals = order_sum.groupby("order_id", as_index=False)["сумма позиции"].sum()
    order_totals = order_totals.rename(columns={"сумма позиции": "сумма заказа"})
    orders_loc = orders.drop(columns=["сумма заказа"], errors='ignore')
    orders_loc = orders.merge(order_totals, on="order_id", how="left")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.scatterplot(data=orders_loc, y="сумма заказа", x="дата_время", hue="тип клиента", palette="viridis")
    plt.title("Распределение суммы заказа по времени и типам клиентов")

    #Создаем группу кнопок
    frame = tk.Frame(new_window, bg=config["bg_color"])
    frame.pack(anchor="n")

    #Создаем кнопку
    button = tk.Button(frame, 
                   text="Обновить", 
                   command=lambda: upd_sum_scatter(ax, canvas))
    button.pack(side="left", pady=5, padx=5)

    #Создаем кнопку сохранения в png
    btn = tk.Button(frame, text="Экспорт в png", command=lambda: save_png(fig, "scatterplot"))
    btn.pack(side="left", padx=5, pady=5)
    
    #Встраиваем график в ткинтер окно
    canvas = FigureCanvasTkAgg(fig, master=new_window)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)
    
    #ссылки
    new_window.fig = fig
    new_window.ax = ax
    new_window.canvas = canvas


def orders_by_hour_text(root):
    """
    

    Parameters
    ----------
    root : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    new_window = tk.Toplevel(root)
    new_window.configure(bg=config["bg_color"])

    #Создаем заголовок
    label = tk.Label(new_window, text="Количество заказов по часам", font=(config["font_family"], config["font_size"], "bold"), bg=config["bg_color"])
    label.pack(pady=10)

    label = tk.Label(new_window, text="Введите час для подсчета количества заказов:", font=(config["font_family"], config["font_size"]), bg=config["bg_color"])
    label.pack(pady=10)

    #Выбор часа
    spinbox = tk.Spinbox(new_window, from_=0.0, to=23.0)
    spinbox.pack(pady=10)

    #Считать
    btn = tk.Button(new_window, text="Считать", command=lambda: count_orders_by_hour(new_window, spinbox))
    btn.pack(padx=6, pady=6)



def count_orders_by_hour(new_window, spinbox):
    """
    

    Parameters
    ----------
    new_window : TYPE
        DESCRIPTION.
    spinbox : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    #Подгрузка свежих данных
    reload_data()

    #Удаление старых виджетов
    for widget in new_window.winfo_children()[4:]:
        widget.destroy()

    hour = int(spinbox.get())
    amount = len(orders[orders["дата_время"].dt.hour == hour])
    label = tk.Label(new_window, text="Отчет 1", font=(config["font_family"], config["font_size"], "bold"), bg=config["bg_color"])
    label = tk.Label(new_window, text=f"Количество заказов за {hour}-й час: {amount}", font=(config["font_family"], config["font_size"]), bg=config["bg_color"])
    label.pack(pady=10)

    data = f"Количество заказов за {hour}-й час: {amount}"

    #Сохранение в excel
    btn = tk.Button(new_window, text="Экспорт в Excel", command=save_excel(data, "orders_by_hour"))
    btn.pack(side="left", padx=10)

    #Сохранение в csv
    btn = tk.Button(new_window, text="Экспорт в CSV", command=save_csv(data, "orders_by_hour"))
    btn.pack(side="left", padx=10)
    

def orders_by_cashiers(root):
    """
    

    Parameters
    ----------
    root : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    new_window = tk.Toplevel(root)
    new_window.configure(bg=config["bg_color"])

    #Создаем заголовок
    label = tk.Label(new_window, text="Количество клиентов, обслуженных каждым кассиром", font=(config["font_family"], config["font_size"], "bold"), bg=config["bg_color"])
    label.pack(pady=10)

    label = tk.Label(new_window, text="Введите ФИО кассира для подсчета количества заказов:", font=(config["font_family"], config["font_size"]), bg=config["bg_color"])
    label.pack(pady=10)

    #Поле ввода
    entry = tk.Entry(new_window)
    entry.pack(padx=6, pady=6)

    #Вывод статистики
    btn = tk.Button(new_window, text="Считать", command=lambda: count_orders_by_cashiers(entry, new_window))
    btn.pack(padx=6, pady=6)

def count_orders_by_cashiers(entry, new_window):
    """
    

    Parameters
    ----------
    entry : TYPE
        DESCRIPTION.
    new_window : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    #Подгрузка свежих данных
    reload_data()

    #Удаление старых виджетов
    for widget in new_window.winfo_children()[4:]:
        widget.destroy()

    #Формирование и заполнение Treeview
    cashier = entry.get()
    mg = orders.merge(cashiers, left_on="кассир", right_on="cashier_id", how="left")
    mg_new = mg.groupby("ФИО").count().reset_index()
    mg_new["процент заказов"] = round((mg_new["кассир"] / 250) * 100, 2)

    mg_show = mg_new[["ФИО", "кассир", "процент заказов"]]

    tree = ttk.Treeview(new_window, columns=list(mg_show.columns), show="headings")

    for col in mg_show.columns:
        tree.heading(col, text=col)

    for _, row in mg_show.iterrows():
        tree.insert("", "end", values=list(row))

    tree.pack(expand=True, fill="both")

    #Сатитстика заказов по кассиру
    res = mg_new[mg_new["ФИО"] == cashier]
    if not res.empty:
        label = tk.Label(new_window, text=f"количество заказов принятых кассиром: {res.iloc[0]['кассир']}", font=(config["font_family"], config["font_size"]), bg=config["bg_color"])
    else:
        label = tk.Label(new_window, text="кассир не найден", font=(config["font_family"], config["font_size"]), bg=config["bg_color"])

    label.pack(pady=10)

    data = mg_show

    #Создаем группу кнопок
    frame = tk.Frame(new_window, bg=config["bg_color"])
    frame.pack(anchor="n", pady=20)

    #Сохранение в excel
    btn = tk.Button(frame, text="Экспорт в Excel", command=save_excel(data, "orders_by_cahiers"))
    btn.pack(side="left", padx=10)

    #Сохранение в csv
    btn = tk.Button(frame, text="Экспорт в CSV", command=save_csv(data, "orders_by_cahiers"))
    btn.pack(side="left", padx=10)


def pivot_analyze(root):
    """
    

    Parameters
    ----------
    root : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    new_window = tk.Toplevel(root)
    new_window.configure(bg=config["bg_color"])

    #Создаем заголовок
    label = tk.Label(new_window, text="Количество блюд разных категорий по часам", font=(config["font_family"], config["font_size"], "bold"), bg=config["bg_color"])
    label.pack(pady=10)

    btn = tk.Button(new_window, text="Обновить", command=lambda: upd_pivot_analyze(new_window))
    btn.pack(padx=6, pady=6)



def upd_pivot_analyze(new_window):
    """
    

    Parameters
    ----------
    new_window : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    #Подгрузка свежих данных
    reload_data()

    #Создание Treeview
    orders['час заказа'] = orders['дата_время'].dt.hour
    order_sum = order.merge(menu, left_on="позиция", right_on="dish_id", how="inner")
    order_sum = order_sum.merge(orders[['order_id', 'час заказа']], on='order_id', how='left')
    pivot = pd.pivot_table(order_sum, index='час заказа', columns='категория', values='позиция', aggfunc='count', fill_value=0)

    pivot = pivot.reset_index()

    tree = ttk.Treeview(new_window, columns=list(pivot.columns), show="headings")

    for col in pivot.columns:
        tree.heading(col, text=col)

    for _, row in pivot.iterrows():
        tree.insert("", "end", values=list(row))

    tree.pack(expand=True, fill="both")

    data = pivot

    #Создаем группу кнопок
    frame = tk.Frame(new_window, bg=config["bg_color"])
    frame.pack(anchor="n", pady=20)

    #Сохранение в excel
    btn = tk.Button(frame, text="Экспорт в Excel", command=save_excel(data, "pivot"))
    btn.pack(side="left", padx=10)

    #Сохранение в csv
    btn = tk.Button(frame, text="Экспорт в CSV", command=save_csv(data, "pivot"))
    btn.pack(side="left", padx=10)

def upd_price_boxplot(ax, canvas):
    """
    

    Parameters
    ----------
    ax : TYPE
        DESCRIPTION.
    canvas : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    #Подгрузка свежих данных
    reload_data()

    # Очищаем график
    ax.clear()
    
    # Рисуем новые данные
    sns.boxplot(data=menu, y="цена", x="категория", ax=ax)
    ax.set_title("Разброс цен по категориям блюд")
    
    # Перерисовываем
    canvas.draw()


def upd_sum_scatter(ax, canvas):
    """
    

    Parameters
    ----------
    ax : TYPE
        DESCRIPTION.
    canvas : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    #Подгрузка свежих данных
    reload_data()

    # Обновляем данные
    order_sum = order.merge(menu, left_on="позиция", right_on="dish_id", how="inner")
    order_sum["сумма позиции"] = order_sum["количество"] * order_sum["цена"]
    order_totals = order_sum.groupby("order_id", as_index=False)["сумма позиции"].sum()
    order_totals = order_totals.rename(columns={"сумма позиции": "сумма заказа"})
    orders_loc = orders.drop(columns=["сумма заказа"], errors='ignore')
    orders_loc = orders.merge(order_totals, on="order_id", how="left")

    # Очищаем график
    ax.clear()
    
    # Рисуем новые данные
    sns.scatterplot(data=orders_loc, y="сумма заказа", x="дата_время", hue="тип клиента", palette="viridis")
    ax.set_title("Распределение суммы заказа по времени и типам клиентов")
    
    # Перерисовываем
    canvas.draw()


def upd_type_of_pay(ax, canvas):
    """
    

    Parameters
    ----------
    ax : TYPE
        DESCRIPTION.
    canvas : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    #Подгрузка свежих данных
    reload_data()

    # Обновляем данные
    mg_1 = orders.merge(client_type, left_on="тип клиента", right_on="type_id", how="inner")
    
    # Очищаем график
    ax.clear()
    
    # Рисуем новые данные
    sns.countplot(data=mg_1, x="тип", hue="тип оплаты ", ax=ax)
    ax.set_title("Типы оплаты по категориям клиентов")
    
    # Перерисовываем
    canvas.draw()

    
def upd_orders_by_hour(ax, canvas):
    """
    

    Parameters
    ----------
    ax : TYPE
        DESCRIPTION.
    canvas : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    #Подгрузка свежих данных
    reload_data()

    # Очищаем график
    ax.clear()
    
    # Рисуем новые данные
    sns.histplot(data=orders, x="дата_время", bins=20, kde=True, color="purple", ax=ax)
    ax.set_title("Распределение заказов по часам")
    
    # Перерисовываем
    canvas.draw()

def info(root):
    """
    

    Parameters
    ----------
    root : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    new_window = tk.Toplevel(root)
    new_window.configure(bg=config["bg_color"])

    text_info = """
    Данное информационно-аналитическое приложение предназначено для визуализации и анализа данных заказов в кофейне.
    С помощью приложения пользователь может получить статистику по количеству и времени заказов, распределение цен, а также статистику заказов по кассирам и типам клиентов. 
    Приложение обеспечивает удобный графический интерфейс с возможностью интерактивного обновления и экспорта отчетов в файлы разных форматов

    Графические отчеты
    Типы оплаты по категориям клиентов – частота разных типов оплаты в зависимости от категории клиентов
    Распределение заказов по часам  - график количества заказов в разные часы дня
    Разброс цен по категориям блюд – распределение цен по категориям меню
    Распределение суммы заказа по времени и типам клиентов  - точечный график, показывающий зависимость суммы заказа от типа клиентов и времени дня
    
    Текстовые отчеты
    Количество заказов по часам  - вывод количества заказов за конкретный час
    Количество блюд разных категорий по часам - сводная с заказами блюд разных категорий
    Количество заказов по кассирам  - статистика принятых заказов по кассирам
    
    Базы данных
    Функционал редактирования базы данных:
    Добавить – добавление строки базы данных снизу
    Удалить – удаление строки базы данных по клику
    Сохранить – сохранение изменений в базе данных
    Экспорт в Excel – сохранение в формате Excel
    
    В окнах доступны кнопки:
    Обновить — обновление графиков с подгрузкой актуальных данных
    Экспорт в png — сохранение текущего графика в файл формата .png в каталог graphics
    Экспорт в Excel/CSV — сохранение отчетов (таблиц или текстовых данных) в соответствующих форматах. Файлы сохраняются в папку output каталога приложения
    Все экспортированные отчеты сохраняются в каталогах graphics и/или output и доступны для просмотра в сторонних приложениях.
    """
    #Обычная метка
    label = tk.Label(new_window, text="О приложении", font=(config["font_family"], config["font_size"], "bold"), bg=config["bg_color"])
    label.pack(padx=10)

    #Метка с выравниванием по левому краю многострочного текста
    label = tk.Label(new_window, text=text_info, font=(config["font_family"], config["font_size"]), bg=config["bg_color"], anchor="w", justify="left")
    label.pack(padx=10, pady=10, fill="x")