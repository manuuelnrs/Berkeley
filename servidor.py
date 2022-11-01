'''
>	@author Nava Rosales Juan Manuel && Hernandez Martinez Miguel Angel 
>	@date 04/octubre/2022
>	@brief Algoritmo Berkeley - Proceso Servidor
>	@version 1.0 
'''
from dateutil import parser
import datetime
import time
import threading
import socket
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')

# Variables globales del servidor
relojLocal = datetime.datetime.now()
AJUSTE = datetime.timedelta(0,0,0)
clientes = {} # Estructura con la información de los clientes

# Funcion principal de Servidor
def Servidor(port):
  relojl = threading.Thread( target = reloj, args = () ) 
  relojl.start() # Inicia Hilo (sub-proceso) de actualizacion de reloj local

  servidor = socket.socket()# Asignación de OBJ Socket
  servidor.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1) # Bandera socket prevención de "TIME_WAIT"
  servidor.bind(('', port)) # Enlace a la dirección
  servidor.listen(10)       # Habilitar conexiones (backlog=10)

  input("[Ingrese enter para ACTIVAR Berkeley]\n")
  initConexion(servidor)    # Aceptacion de conexiones (Clientes)


def initConexion(servidor): # Recepcion de conexiones Clientes
  global relojLocal
  
  sincronizacion = threading.Thread(target=sincronizarRelojes, args=())
  sincronizacion.start()

  while True:
    conexion, dir = servidor.accept()     # Acepta conexion Cliente
    IPort = str(dir[0]) + ":" + str(dir[1])  # Direción del Cliente (host + port)
    logging.info( f"Conexión exitosa con el Cliente: {IPort}" ) # Conexión realizada
    conexion.send((str("RS")+str(relojLocal)).encode()) # Envia reloj local a Clientes

    berkley = threading.Thread(target = control_relojes, args = ( conexion, IPort, ))
    berkley.start()    # Iniciar Hilo (sub-proceso) envio/recepcion de relojes para sincronizar

def control_relojes(conexion, IPort):
  while True:
    try:
      reloj = conexion.recv(1024).decode()
      if reloj:
        if reloj[:2] == "DF": # Recibe diferencia reloj #
          logging.info( f"Recepcion de diferencia de reloj ({IPort})" )
          diferenciaR = parser.parse(reloj[2:])
          diferenciaR = diferenciaR - datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
          clientes[IPort] = {"diferencia" : diferenciaR, "conexion" : conexion }

    except:
      del clientes[IPort]
      conexion.close()
      break

def sincronizarRelojes():
  global AJUSTE
  while True:
    logging.info( f"Sincronizando {len(clientes)} relojes..." )
    if len(clientes) > 0: # Si hay mas de un Cliente en conexión, sincroniza
      prom_difRelojes = promedioRelojes() # Obtener el promedio de la diferencia de Relojes
      logging.info( f"Ajuste de reloj: {prom_difRelojes} << Sincronizando >>")
      AJUSTE = prom_difRelojes        # Ajuste del reloj local (servidor)
      for IP, cliente in clientes.items():# Sincornizar PARA cada Cliente conectado al servidor
        try:
          difCL = cliente['diferencia']
          ajusteCL = difCL  - prom_difRelojes if (difCL  > prom_difRelojes) else prom_difRelojes - difCL
          cliente['conexion'].send( (str("RA")+str(ajusteCL)).encode() )   # Enviar al Cliente diferencia sincronizada
        except:
          logging.DEBUG( f"Ocurrió un error al sincronizar tiempo de Cliente: {IPort}" ) # Error al sincronizar
    time.sleep(5)

def promedioRelojes():
  diferenciasReloj = list(cliente['diferencia'] for IPort, cliente in clientes.items()) # Listas diferencias de CLientes
  sumaDiferenciasReloj = sum(diferenciasReloj, datetime.timedelta(0,0)) # Sumar (iteracion) las diferencias de clientes
  prom_difRelojes = sumaDiferenciasReloj / ( len(clientes)+1 ) # Promedio de las diferencias de relojes + 1(servidor)
  logging.debug( f"Promedio de las diferencias de reloj: {prom_difRelojes}" )
  return prom_difRelojes # Devuelve el promedio de Relojes

def reloj():
  global relojLocal
  while True:
    relojLocal = datetime.datetime.now() + AJUSTE
    print(relojLocal.strftime("[%I:%M:%S]")) # Impresion de reloj local
    time.sleep(1)

if __name__ == '__main__':
  Servidor(port = 8000)