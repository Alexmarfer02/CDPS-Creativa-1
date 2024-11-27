import logging, os, subprocess
from subprocess import call

log = logging.getLogger('manage-p2')


class VM:
    def __init__(self, name):
        self.name = name
        log.debug(f'Initializing VM {name}')
        
    def create(self, image, interfaces):
        log.debug(f'Creating VM {self.name} with image {image} and interfaces {interfaces}')
        # Implementar comandos para crear XML, discos y configuración
    
    def start(self):
        log.debug(f'Starting VM {self.name}')
        # Comando para iniciar VM
    
    def stop(self):
        log.debug(f'Stopping VM {self.name}')
        # Comando para detener VM
    
    def destroy(self):
        log.debug(f'Destroying VM {self.name}')
        # Comando para destruir VM


class NET:
    def __init__(self, name):
        self.name = name
        log.debug(f'Initializing Network {name}')
        
    def create(self):
        log.debug(f'Creating Network {self.name}')
        # Crear bridges con ovs-vsctl
    
    def destroy(self):
        log.debug(f'Destroying Network {self.name}')
        # Destruir bridges