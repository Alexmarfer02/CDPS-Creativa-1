
from lib_vm import MV
from lxml import etree
import logging, sys, json
import os
from subprocess import call

with open('manage-p2.json', 'r') as file:
    data = json.load(file)

if data["num_serv"] > 5 or data["num_serv"] < 1:
    print("Número de servidores inválido, introduzca en su archivo de configuración un número de servidores de 1 a 5.")
else:
    num_serv = data["num_serv"]