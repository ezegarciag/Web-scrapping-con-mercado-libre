import tkinter as tk
from tkinter import simpledialog

import requests
from bs4 import BeautifulSoup
import re
import csv
import os
import pandas as pd


def obtener_datos_scrapping(nombre_producto):
    string = nombre_producto
    paginas_a_buscar = int(entrada_paginas.get())

    busqueda_url = string.replace(" ", "-")
    url = f"https://listado.mercadolibre.com.ar/{busqueda_url}#D[A:{busqueda_url}]"
    scrapping(string,url, 1)

    desde = 51
    pagina = 2
    for i in range(paginas_a_buscar - 1):
        url = f"https://listado.mercadolibre.com.ar/{string}_Desde_{desde}_NoIndex_True"
        scrapping(string,url, pagina)
        pagina += 1
        desde += 50

    limpia_csv(string)
    duplicados(string)
    etiqueta_estado.config(text="Scrapping completado y datos procesados con éxito.")



def escribe_csv(nombre,lista, pagina):
    for i in range(len(lista)):
        lista[i] = (lista[i][0], lista[i][1].replace('.', '') if '.' in lista[i][1] else lista[i][1], lista[i][2])
    
    # Crear un DataFrame con los datos de la lista
    df = pd.DataFrame(lista, columns=['producto', 'precio', 'links'], dtype=str)
    
    # Agregar una columna para la página
    df['pagina'] = pagina

    # Leer el archivo CSV existente si hay uno
    try:
        existing_df = pd.read_csv(f'{nombre}.csv', dtype=str)
    except FileNotFoundError:
        existing_df = pd.DataFrame(columns=['producto', 'precio', 'links', 'pagina'])

    # Concatenar el DataFrame existente y el nuevo
    combined_df = pd.concat([existing_df, df], ignore_index=True)

    # Escribir el DataFrame en el archivo CSV
    combined_df.to_csv(f'{nombre}.csv', index=False, encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)


def scrapping(nombre,link, pagina):
    r = requests.get(link)
    contenido = r.content

    soup = BeautifulSoup(contenido, "html.parser")

    all_divs = soup.find_all(class_=re.compile(".*andes-card.*"))
    # Definir listas para almacenar productos y precios
    lista_productos = []
    lista_precios = []
    lista_links = []

    # Iterar sobre todos los elementos <div> de los productos
    for item in all_divs:

        # Obtener el nombre del producto
        nombre_producto_element = item.find('h2', {'class': 'ui-search-item__title'})
        nombre_producto = nombre_producto_element.text.strip() if nombre_producto_element is not None else "Nombre no disponible"

        # Obtener el precio del producto
        precio_producto_element = item.find('span', {'class': 'andes-money-amount__fraction'})
        precio_producto = str(precio_producto_element.text.strip()) if precio_producto_element is not None else "Precio no disponible"

        
        enlace = item.find('a', {'class': 'ui-search-item__group__element ui-search-link__title-card ui-search-link'})
        if enlace:
            link = enlace.get('href')
        #else:
           # print("No se encontró el enlace con la clase especificada.") # no encontro el enlace

        # Agregar el nombre y el precio a las listas correspondientes
        lista_productos.append(nombre_producto)
        lista_precios.append(precio_producto)
        lista_links.append(link)

    lista_productos_con_precios = list(zip(lista_productos, lista_precios, lista_links))
    escribe_csv(nombre,lista_productos_con_precios, pagina)


def limpia_csv(nombre):
    # Leer el archivo CSV
    try:
        df = pd.read_csv(f'{nombre}.csv')
    except FileNotFoundError:
        print("El archivo CSV no existe.")
        return

    # Eliminar filas con 'no disponible' en la columna 'producto'
    df = df[df['producto'] != 'Nombre no disponible']

    # Reindexar el DataFrame para asegurarse de que no haya índices faltantes
    df.reset_index(drop=True, inplace=True)

    # Escribir el DataFrame limpio de nuevo al archivo CSV
    df.to_csv(f'{nombre}.csv', index=False, encoding='utf-8')


def duplicados(nombre):
    # Leer el archivo CSV en un DataFrame
    df = pd.read_csv(f'{nombre}.csv')

    # Encontrar filas duplicadas basadas en la columna 'links'
    duplicados = df.duplicated(subset=['links'], keep=False)

    # Contar el número total de filas duplicadas
    num_duplicados = duplicados.sum()

    print("Número total de filas duplicadas basadas en el enlace:", num_duplicados)

    # Filtrar el DataFrame original con las filas duplicadas
    filas_duplicadas = df[duplicados]

    print("Filas duplicadas basadas en el enlace:")
    print(filas_duplicadas)


# Crear ventana principal
ventana = tk.Tk()
ventana.title("Web Scrapping MercadoLibre")

# Crear etiquetas y campos de entrada
etiqueta_producto = tk.Label(ventana, text="Producto:")
etiqueta_producto.grid(row=0, column=0, padx=5, pady=5)

entrada_producto = tk.Entry(ventana)
entrada_producto.grid(row=0, column=1, padx=5, pady=5)

etiqueta_paginas = tk.Label(ventana, text="Páginas a buscar:")
etiqueta_paginas.grid(row=1, column=0, padx=5, pady=5)

entrada_paginas = tk.Entry(ventana)
entrada_paginas.grid(row=1, column=1, padx=5, pady=5)

# Botón para ejecutar el web scrapping
boton_scrapping = tk.Button(ventana, text="Ejecutar Scrapping", command=lambda: obtener_datos_scrapping(entrada_producto.get()))
boton_scrapping.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Etiqueta para mostrar el estado del proceso
etiqueta_estado = tk.Label(ventana, text="")
etiqueta_estado.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

# Ejecutar la ventana
ventana.mainloop()
