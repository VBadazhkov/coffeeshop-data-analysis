# -*- coding: utf-8 -*-
"""
Created on Sat May 31 22:16:57 2025

@author: Влад
"""

import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk


#Сохранение файлов в форматах png, excel, csv
def save_png(data, name):
    """
    

    Parameters
    ----------
    data : TYPE
        DESCRIPTION.
    name : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    plt.savefig(f"C:/work/graphics/{name}.png")

def save_excel(data, name):
    """
    

    Parameters
    ----------
    data : TYPE
        DESCRIPTION.
    name : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    if isinstance(data, pd.DataFrame):
        data.to_excel(f"C:/work/output/{name}.xlsx")
    else:
        df = pd.DataFrame({"Данные": [data]})
        df.to_excel(f"C:/work/output/{name}.xlsx")

def save_csv(data, name):
    """
    

    Parameters
    ----------
    data : TYPE
        DESCRIPTION.
    name : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    if isinstance(data, pd.DataFrame):
        data.to_csv(f"C:/work/output/{name}.csv", index=False, sep=";", encoding="utf-8-sig")
    else:
        df = pd.DataFrame({"Данные": [data]})
        df.to_csv(f"C:/work/output/{name}.csv", index=False, sep=";", encoding="utf-8-sig")

#Заполнение виджета Treeview
def fill_treeview(new_window, data, tree):
    """
    

    Parameters
    ----------
    new_window : TYPE
        DESCRIPTION.
    data : TYPE
        DESCRIPTION.
    tree : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    for col in data.columns:
        tree.heading(col, text=col)

    for idx, (_, row) in enumerate(data.iterrows()):
        tree.insert("", "end", iid=str(idx), values=list(row))

    # Прокрутка к последней строке
    if tree.get_children():
        tree.see(tree.get_children()[-1])

    #Инициируем прокрутку
    scrollbar = tk.Scrollbar(new_window, command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.config(yscrollcommand=scrollbar.set)

#Обновление таблицы (виджет Treeview)
def refresh_tree(tree, database):
    """
    

    Parameters
    ----------
    tree : TYPE
        DESCRIPTION.
    database : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    tree.delete(*tree.get_children())
    for idx, row in database.iterrows():
        tree.insert("", "end", iid=str(idx), values=list(row))

    # Показать последнюю строку
    if tree.get_children():
        tree.see(tree.get_children()[-1])

#Сохранение в файл формата pickle
def save_pickle(data, name):
    """
    

    Parameters
    ----------
    data : TYPE
        DESCRIPTION.
    name : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    data.to_pickle(f"C:/work/data/{name}.pick")


