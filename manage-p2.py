

from lxml import etree
import logging, sys, json
import os
from subprocess import call
from lib_vm import VM, NET

# with open('manage-p2.json', 'r') as file:
#     data = json.load(file)

# if data["num_serv"] > 5 or data["num_serv"] < 1:
#     print("Número de servidores inválido, introduzca en su archivo de configuración un número de servidores de 1 a 5.")
# else:
#     num_serv = data["num_serv"]

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
    c1 = VM("c1")
    c1.crear_mv()
    lb = VM("lb")
    lb.crear_mv()

    for n in range(1, numero):
        #numaquina = str(n)
        nombre = f"s{n}"
        servidor = VM(str(nombre))
        servidor.crear_vm()

# Main
init_log()
print('CDPS - mensaje info1')

