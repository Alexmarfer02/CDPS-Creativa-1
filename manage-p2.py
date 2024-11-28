from lxml import etree
import logging, sys, json
import os
from subprocess import call
from lib_vm import VM, RED

log = logging.getLogger('manage-p2')

with open('manage-p2.json', 'r') as json:
    data = json.load(json)

numero = data["number_of_servers"]


def init_log():
    # Creacion y configuracion del logger
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger('manage-p2')
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.propagate = False

def pause():
    programPause = input("-- Press <ENTER> to continue...")


def create():
    c1 = VM("c1") #crear objeto clase VM
    c1.create_vm() #LLAMAS AL METODO...
    lb = VM("lb")
    lb.create_vm()

    if numero > 5 or numero < 1:
        log.error("Número de servidores inválido, introduzca un número de servidores de 1 a 5.")
        return
    log.debug("Numero de vm valido")
    
    for n in range(1, numero):
        #numaquina = str(n)
        nombre = f"s{n}"
        servidor = VM(nombre)
        servidor.create_vm()
    
    LAN1 = RED('LAN1')
    LAN1.create_red()
    LAN2 = RED('LAN2')
    LAN2.create_red()
    call(["sudo", "ifconfig", "LAN1", "10.11.1.3/24"])###CAMBIARip
    call(["sudo", "ip", "route", "add", "10.11.0.0/16", "via", "10.11.1.1"])###CAMBIARip

    log.debug("Escenario creado correctamente")

def start():
    
        for n in range(1, numero + 1):
            nombre = f"s{n}"
            s = VM(nombre) #inglés?
            s.start_vm()
            s.show_console_vm()
            log.info(f"{nombre} iniciado correctamente.")
        
        # Iniciar  c1
        c1 = VM("c1")
        c1.start_vm()
        c1.show_console_vm()
        log.info("c1 iniciado correctamente.")

        # Iniciar router lb
        lb = VM("lb")
        lb.start_vm()
        lb.show_console_vm()
        #log.info("Router 'lb' iniciado correctamente.")

    #log.debug("Escenario arrancado correctamente")

def stop():
    
    for n in range(1, numero + 1):
            nombre = f"s{n}"
            servidor = VM(nombre)
            servidor.stop_vm()
            
    c1 = VM("c1")
    c1.stop_vm() 
    
    lb = VM("lb")
    lb.stop_vm()


def destroy():
    
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

