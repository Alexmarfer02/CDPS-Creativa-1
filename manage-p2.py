
from lib_vm import VM, RED
from lxml import etree
import logging, sys, json
import os
from subprocess import call

with open('manage-p2.json', 'r') as file:
    data = json.load(file)

if data["number_of_servers"] > 5 or data["number_of_servers"] < 1:
    print("Número de servidores inválido, introduzca en su archivo de configuración un número de servidores de 1 a 5.")
else:
    num_serv = data["number_of_servers"]
    
def init_log():
    # Creacion y configuracion del logger
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger('auto_p2')
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.propagate = False

def pause():
    programPause = input("-- Press <ENTER> to continue...")

def create(numero):
    c1 = VM("c1") #crear objeto clase VM
    c1.crear_vm() #LLAMAS AL METODO...
    lb = VM("lb")
    lb.crear_vm()

    for n in range(1, numero):
        #numaquina = str(n)
        nombre = f"s{n}"
        servidor = VM(nombre)
        servidor.crear_vm()
    
    LAN1 = RED('LAN1')
    LAN1.create_red()
    LAN2 = RED('LAN2')
    LAN2.create_red()
    call(["sudo", "ifconfig", "LAN1", "10.11.1.3/24"])###CAMBIARip
    call(["sudo", "ip", "route", "add", "10.11.0.0/16", "via", "10.11.1.1"])###CAMBIARip

    #logger.debug("Escenario creado correctamente")

def start(numero):
    
        for n in range(1, numero + 1):
            nombre = f"s{n}"
            servidor = VM(nombre)
            servidor.start_vm()
            #log.info(f"Servidor '{vm_name}' iniciado correctamente.")
        
        # Iniciar cliente c1
        c1 = VM("c1")
        c1.start_vm()
        #log.info("Cliente 'c1' iniciado correctamente.")

        # Iniciar router lb
        lb = VM("lb")
        lb.start_vm()
        #log.info("Router 'lb' iniciado correctamente.")

    #log.debug("Escenario arrancado correctamente")

def stop(numero):

    for n in range(1, numero + 1):
            nombre = f"s{n}"
            servidor = VM(nombre)
            servidor.stop_vm()
            
    c1 = VM("c1")
    c1.stop_vm()

    lb = VM("lb")
    lb.stop_vm()


def destroy(numero):
    
    for n in range(1, numero + 1):
            nombre = f"s{n}"
            servidor = VM(nombre)
            servidor.destroy_vm()  
        
    c1 = VM("c1")
    c1.destroy_vm()  
        
    lb = VM("lb")
    lb.destroy_vm()  
        #log.info("Router 'lb' destruido correctamente.")
        
        # Destruir redes LAN1 y LAN2
    LAN1 = RED("LAN1")
    LAN2 = RED("LAN2")
    LAN1.destroy_red()  
    LAN2.destroy_red()  
    
        #log.info("Redes 'LAN1' y 'LAN2' eliminadas correctamente.")


    #log.debug("Escenario destruido correctamente.")

# Main
init_log()
print('CDPS - mensaje info1')
    
    
