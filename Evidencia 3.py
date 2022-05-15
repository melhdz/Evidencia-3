#Librerias
from collections import namedtuple
import os
from datetime import datetime as dt
import sys
from prettytable import PrettyTable
import sqlite3
from sqlite3 import Error

LimpiarPantalla = lambda: os.system('cls')
monto_total = 0

def separador():
    print("*" * 20)

#Base de datos y menú
try:
    with sqlite3.connect("servicios.db") as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS servicio (clave INTEGER PRIMARY KEY, fecha TEXT NOT NULL, cliente TEXT NOT NULL) ")
        c.execute("CREATE TABLE IF NOT EXISTS equipo (descripcion TEXT NOT NULL, cobro REAL NOT NULL, id_servicio INTEGER NOT NULL, FOREIGN KEY(id_servicio) REFERENCES servicio(clave)) ")
except Error as e:
    print(e)
except Exception:
    print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
finally:
    if conn:
        conn.close()
while True:
    LimpiarPantalla()
    print("---SERVICIOS---")
    print("¿Qué desea hacer?")
    print("A: Contratar servicio")
    print("B: Consultar servicio")
    print("C: Servicios en una fecha")
    print("D: Clientes atendidos en rango de fechas")
    print("E: Salir")
    try:
        opcion = input("Ingrese una opción: ")
        if opcion.upper() == "A":
            monto_total = 0
            try:
                with sqlite3.connect("servicios.db") as conn: #Puente
                    c = conn.cursor()
                # Validar que clave no exista
                    switch = True
                    clave = int(input("Ingrese la clave del servicio: "))
                    c.execute("SELECT COUNT(*) FROM equipo WHERE id_servicio = ?",(clave,))
                    clave_valida = c.fetchall()
                    clave_valida = clave_valida[0]
                    if clave_valida[0]>=1:
                        input("Error: La clave ya existe...")
                    else:
                        while switch:
                            while True:
                                equipo = input("Ingrese la descripción del equipo: ")
                                if equipo == "":
                                    print("Este dato no puede ser vacío")
                                else:
                                    break
                            while True:
                                try: #Valida que se ingrese un numero
                                    precio = float(input("Ingrese el precio del equipo: "))
                                except Exception:
                                    print(f"Ocurrió un problema, debe ingresar un dato numérico de tipo entero o float: {sys.exc_info()[0]}")
                                    input("Pulse enter para continuar... ")
                                else:
                                    break
                            datos_equipo = equipo,precio,clave
                            c.execute("INSERT INTO equipo VALUES(?,?,?)",datos_equipo)
                            print("Registro agregado exitosamente!")

                            monto_total = monto_total + precio
                            while True:
                                respuesta = input("¿Desea agregar otro equipo? [S/N]: ")
                                if respuesta.upper() == "S":
                                    LimpiarPantalla()
                                    break
                                elif respuesta.upper() == "N":
                                    switch = False
                                    LimpiarPantalla()
                                    while True:
                                        nom_servicio = input("Ingrese descripcion de servicio: ")
                                        if nom_servicio == "":
                                            print("No se puede omitir el nombre del servicio")
                                        else:
                                            break
                                    while True:
                                        cliente = input("Ingrese el nombre del cliente: ")
                                        if cliente == "":
                                            print("No se puede omitir el nombre del cliente")
                                        else:
                                            break
                                    #Se almacena la fecha, se calcula el monto, luego se carga al diccionario
                                    fecha_procesada = dt.today().strftime('%d/%m/%Y')
                                    c.execute("INSERT INTO servicio VALUES(?,?,?)",(clave, fecha_procesada, cliente))

                                    IVA = (monto_total * 0.16)
                                    print(f'El monto total a pagar por el servicio es: {"${:,.2f}".format((monto_total + IVA))}')
                                    print(f'El IVA del 16% aplicado al total es: {"${:,.2f}".format((IVA))}')
                                    input("Presiona enter para volver a menú ")
                                    break
                                else:
                                    print("Error: Opcion no valida.")
                if conn:
                    conn.close()
            except:
                print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
        elif opcion.upper() == "B":
            LimpiarPantalla()
            monto_total_consulta = 0
            clave = int(input("Ingrese la clave que desea buscar: "))
            try:
                with sqlite3.connect("servicios.db") as conn: #Puente
                    mi_cursor = conn.cursor() #Mensajero
                    mi_cursor.execute("SELECT s.*, e.* FROM servicio as s,equipo as e WHERE s.clave = (?) AND e.id_servicio = (?)",(clave,clave))
                    registros = mi_cursor.fetchall()
                    t = PrettyTable(['Clave','Fecha','Cliente','Descripcion','Cobro','Id_Servicio'])
                    for clave,fecha,cliente,descripcion,cobro,id_servicio in registros:
                        t.add_row([clave,fecha,cliente,descripcion,cobro,id_servicio])
                        monto_total_consulta = monto_total_consulta + cobro
                    print(t)
                    IVA = monto_total_consulta * 0.16
                    print(f"Monto:  {'${:,.2f}'.format(monto_total_consulta)}")
                    print(f"Monto total: {'${:,.2f}'.format(monto_total_consulta + IVA)}")
                    print(f"El IVA aplicado del 16% fue: {'${:,.2f}'.format(IVA)}")
                    separador()
                    input("Presiona enter para volver a menú ")
                if conn:
                    conn.close()
            except Error as e:
                print (e)
            except Exception:
                print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
        elif opcion.upper() == 'C':
            LimpiarPantalla()
            fecha_buscar = input("Ingrese la fecha a buscar en formato DD/MM/AAAA: ")
            try:
                with sqlite3.connect("servicios.db") as conn: #Puente
                    mi_cursor = conn.cursor() #Mensajero
                    mi_cursor.execute("SELECT DISTINCT e.id_servicio,e.descripcion,e.cobro FROM equipo as e, servicio as s WHERE s.fecha = ?",(fecha_buscar,))
                    registros = mi_cursor.fetchall()
                    t = PrettyTable(['Clave','Descripcion','Cobro'])
                    for clave,descripcion,cobro in registros:
                        t.add_row([clave,descripcion,cobro])
                    print(t)

                    mi_cursor.execute("SELECT clave FROM servicio")
                    cant_registros = mi_cursor.fetchall()

                    print("---Monto total por clave---")
                    t = PrettyTable(['Clave','Monto','IVA','Gran Total'])
                    for clave in cant_registros:
                        mi_cursor.execute("SELECT e.id_servicio as clave, SUM(cobro) as monto FROM equipo as e WHERE e.id_servicio = ?",clave)
                        registros = mi_cursor.fetchall()
                        for clave,monto in registros:
                            iva = monto * 0.16
                            monto_total = monto + iva
                            t.add_row([clave,monto,iva,monto_total])
                    print(t)
                    input("Presiona enter para volver a menú ")
                if conn:
                    conn.close()
            except Error as e:
                print (e)
            except Exception:
                print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
        elif opcion.upper() == "D":
            fecha_inicio = input("Ingrese la fecha inicio a buscar en formato DD/MM/AAAA: ")
            fecha_fin = input("Ingrese la fecha fin a buscar en formato DD/MM/AAAA: ")
            try:
                with sqlite3.connect("servicios.db") as conn: #Puente
                    mi_cursor = conn.cursor() #Mensajero
                    mi_cursor.execute("SELECT clave, cliente FROM servicio WHERE fecha BETWEEN (?) and (?)",(fecha_inicio, fecha_fin))
                    registros = mi_cursor.fetchall()
                    t = PrettyTable(['Clave','Cliente'])
                    for clave,cliente in registros:
                        t.add_row([clave,cliente])
                    print(t)
                    input("Presiona enter para volver a menú ")
                if conn:
                    conn.close()
            except Error as e:
                print (e)
            except Exception:
                print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
        elif opcion.upper() == "E":
            break
        else:
            print("Opcion no valida")
            input("Pulse enter para continuar... ")
    except ValueError:
        print('Ingrese un dato numérico entero. ')
        input("Pulse enter para continuar... ")

