# -*- coding: utf-8 -*-
"""
Created on Sat May 31 22:16:57 2025

@author: Влад
"""

import tkinter as tk
import sys
import os
import pandas as pd
from pathlib import Path


sys.path.append(str(Path(__file__).parent.parent)) 

from scripts.domain import load_config, type_of_pay, orders_by_hour, price_boxplot, sum_scatter, orders_by_hour_text, orders_by_cashiers, pivot_analyze, cashiers_database, client_types_database, menu_database, order_database, orders_database, info
from library.common import save_csv, save_excel, save_png, save_pickle, fill_treeview, refresh_tree 

os.chdir("C:/work")
cashiers = pd.read_pickle("C:/work/data/cashiers.pick")
client_type = pd.read_pickle("C:/work/data/client_type.pick")
menu = pd.read_pickle("C:/work/data/menu.pick")
order = pd.read_pickle("C:/work/data/order.pick")
orders = pd.read_pickle("C:/work/data/orders.pick")


def create_menu(root): 
    """
    

    Parameters
    ----------
    root : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    #Привязываем главное меню
    menu_bar = tk.Menu(root) 

    #Создаем подменю
    graphic_menu = tk.Menu(menu_bar, tearoff=0)
    text_menu = tk.Menu(menu_bar, tearoff=0)
    databases = tk.Menu(menu_bar, tearoff=0)
    app_info = tk.Menu(menu_bar, tearoff=0)

    #Иниициализируем пункты меню графических отчетов
    graphic_menu.add_command(label="Тип оплаты по категориям клиентов", command=lambda: type_of_pay(root))
    graphic_menu.add_command(label="Распределение заказов по часам", command=lambda: orders_by_hour(root))
    graphic_menu.add_command(label="Разброс цен по категориям блюд", command=lambda: price_boxplot(root))
    graphic_menu.add_command(label="Распределение суммы заказа по времени и типам клиентов", command=lambda: sum_scatter(root))

    #Иниициализируем пункты меню текстовых отчетов
    text_menu.add_command(label="Количество заказов по часам", command=lambda: orders_by_hour_text(root))
    text_menu.add_command(label="Количество заказов по кассирам", command=lambda: orders_by_cashiers(root))
    text_menu.add_command(label="Количество блюд разных категорий по часам", command=lambda: pivot_analyze(root))

    #Иниициализируем пункты меню баз данных
    databases.add_command(label="Кассиры", command=lambda: cashiers_database(root))
    databases.add_command(label="Типы клиентов", command=lambda: client_types_database(root))
    databases.add_command(label="Меню", command=lambda: menu_database(root))
    databases.add_command(label="Состав заказов", command=lambda: order_database(root))
    databases.add_command(label="Заказы", command=lambda: orders_database(root))

    #Инициализируем создание справки
    app_info.add_command(label="Справка", command=lambda: info(root))

    #Добавляем подменю в главное меню с заголовком
    menu_bar.add_cascade(label="Графические отчеты", menu=graphic_menu)
    menu_bar.add_cascade(label="Текстовые отчеты", menu=text_menu)
    menu_bar.add_cascade(label="Базы данных", menu=databases)
    menu_bar.add_cascade(label="Справка", menu=app_info)

    #Прикрепляем главное меню к корню
    root.config(menu=menu_bar)


#создаем главное окно приложения
root = tk.Tk()

#Создаем главное меню
create_menu(root)

#Окно работает пока пользователь его не закроет
root.mainloop()