'''
>	@author Nava Rosales Juan Manuel && Hernandez Martinez Miguel Angel 
>	@date 04/octubre/2022
>	@brief Algoritmo Berkeley - Proceso Cliente
>	@version 1.0 
'''
from dateutil import parser
import datetime
import time
import random
import threading
import socket
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')

# Variable global del Cliente
relojLocal = datetime.datetime.now()
AJUSTE = datetime.timedelta(0,0,0)

# Funcion principal de Cliente
def Cliente(port):
  relojl = threading.Thread( target = reloj, args = () ) # Reloj local
  relojl.start()

  cliente = socket.socket() # Asignación de OBJ Socket
  cliente.connect(('localhost', port)) # Conexion remota al servidor (HOST, PORT)
  logging.info( f"Conexión exitosa con el servidor" )

  recepcion =  threading.Thread( target = recepcionReloj, args = (cliente, ))
  recepcion.start()

def recepcionReloj(cliente): # Recepcion de relojes
  global relojLocal
  global AJUSTE
  while True:
    try:
      reloj = cliente.recv(1024).decode()

      if reloj:
        if reloj[:2] == "RS": # Recibe reloj servidor
          tiempoReloj = parser.parse(reloj[2:])         # Casteo de tiempo de reloj del servidor
          # Diferencia de tiempo de reloj actual
          tiempoReloj_diff = relojLocal - tiempoReloj #if (relojLocal > tiempoReloj) else tiempoReloj - relojLocal
          tiempoRelojtmp = tiempoReloj.strftime("%I:%M:%S")
          logging.info( f"Recepcion de reloj de servidor: {tiempoRelojtmp}" )
          logging.info( f"Envio de diferencia de reloj: {tiempoReloj_diff}" )
          cliente.send((str("DF")+str(tiempoReloj_diff)).encode())  # Enviar diferencia de Reloj local vs servidor

        elif reloj[:2] == "RA": # Recibe reloj Ajuste
          tiempoSincronizado = parser.parse(reloj[2:])  # Casteo de tiempo de ajuste
          AJUSTE = tiempoSincronizado - datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
          tiempoSincronizado = str(tiempoSincronizado.strftime("%I:%M:%S")) # Formateo reloj
          logging.info( f"Recepcion de Ajuste: {AJUSTE} << Sincronizando >>" )
    except:
      print("[Conexion terminada] Ocurrio un error de sincronizacion")
      break

def reloj():
  global relojLocal
  deltaTiempo = relojAleatorio()
  while True:
    relojLocal = datetime.datetime.now() + deltaTiempo - AJUSTE
    print(relojLocal.strftime("[%I:%M:%S]")) # Impresion de reloj local (ALTERADO)
    time.sleep(1)

def relojAleatorio():
    aleatorio = list(range(10,60)) # Lista de (segundos) aleatorios 10 a 60
    #for i in range(-10,11,1):         # Eliminar numeros cercanos al reloj servidor
    #  aleatorio.remove(i)             # Eliminar -10 a 10 segundos extra
    # Devolver reloj modificado (ALEATORIO) al cliente
    return datetime.timedelta(seconds=random.sample(aleatorio,1)[0])

if __name__ == '__main__':
  Cliente(port = 8000)