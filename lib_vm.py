import logging, os, subprocess
from subprocess import call
from lxml import etree

log = logging.getLogger('manage-p2')

#Creamos el escenario 
servers = {"s1", "s2", "s3", "s4", "s5"}
bridges = {"c1":["LAN1"],
          "lb":["LAN1"],
          "s1":["LAN2"],
          "s2":["LAN2"],
          "s3":["LAN2"],
          "s4":["LAN2"],
          "s5":["LAN2"]}
network = {
          "c1":["10.1.1.2", "10.1.1.1"],
          "s1":["10.1.2.11", "10.1.2.1"],
          "s2":["10.1.2.12", "10.1.2.1"], 
          "s3":["10.1.2.13", "10.1.2.1"],
          "s4":["10.1.2.14", "10.1.2.1"],
          "s5":["10.1.2.15", "10.1.2.1"]}


def edit_xml (mv):
    #Se obtiene el directorio de trabajo
    cwd = os.getcwd()  #método de OS que devuelve el Current Working Directory
    path = cwd + "/" + mv
    
    #Se importa el .xml de la máquina pasada como parámetro utilizando métodos de la librería LXML
    tree = etree.parse(path + ".xml")
    root = tree.getroot()
    
    #Se define el nombre de la MV
    name = root.find("name")
    name.text = mv
    
    #Se define el nombre de la imagen, cambiando la ruta del source de la imagen (disk) al qcow2 correspondiente a la maquina pasada como parametro
    sourceFile = root.find("./devices/disk/source")
    sourceFile.set("file", path + ".qcow2")
    
    #Se definen los bridges, modificando el XML con los bridges correspondientes a la maquina parámetro
    bridge = root.find("./devices/interface/source")
    bridge.set("bridge", bridges[mv][0])  #se cambia el valor de la etiqueta <source bridge> por la LAN (el bridge) correspondiente a la máquina pasada como parametro
    
    with open(path + ".xml" ,"w") as xml :
        xml.write(etree.tounicode(root, pretty_print=True))  #Se escribe el XML modificado en el archivo correspondiente a la máquina pasada como parámetro
    
    #Lo hacemos para lb ya que esta en 2 LANs distintas
    if mv == "lb" :
        fin = open(path + ".xml",'r')   #fin es el XML correspondiente a lb, en modo solo lectura
        fout = open("temporal.xml",'w')  #fout es un XML temporal abierto en modo escritura
        for line in fin:
            if "</interface>" in line:
                fout.write("</interface>\n <interface type='bridge'>\n <source bridge='"+"LAN2"+"'/>\n <model type='virtio'/>\n </interface>\n")
    #si el XML de lb contiene un interface (que lo va a contener, ya que previamente se le habrá añadido el bridge LAN1), se le añade al XML temporal otro bridge: LAN2
    else:
        fout.write(line)
    fin.close()
    fout.close()

    call(["cp","./temporal.xml", path + ".xml"])  #sustituimos es XML por el temporal, que es el que contiene las dos LAN
    call(["rm", "-f", "./temporal.xml"])

def config_network(mv):
    cwd = os.getcwd()
    path = cwd + "/" + mv
    
    with open("hostname", "w") as hostname:
        hostname.write(mv + "\n")
        
    call(["sudo", "virt-copy-in", "-a", mv + ".qcow2", "hostname", "/etc"])
    call(["rm", "-f", "hostname"])

class VM:
    def __init__(self, name):
        self.name = name
        log.debug(f'Initializing VM {name}')
        
    def create_vm(self):
        log.debug(f'Creando VM {self.name}')
        #Se crean las MVs y las redes que forman el escenario a partir de la imagen base
        call(["qemu-img","create", "-f", "qcow2", "-b", "./cdps-vm-base-pc1.qcow2",  self.name + ".qcow2"])
        #Se modifican archivos de configuración de las MVs (los xmls)
        call(["cp", "plantilla-vm-pc1.xml", self.name + ".xml"])
        edit_xml(self.name)
        log.debug(f"Fichero {self.name}.xml modificado con éxito.")
        #Definimos las maquinas virtuales
        call(["sudo", "virsh", "define", self.name + ".xml"])
        log.debug(f"Definida MV {self.name}")
        #Configuramos las redes de las maquinas virtuales
        config_network(self.name)
        
    def start_vm(self):
        log.debug(f'Arrancando VM {self.name}')
        #Arrancamos las maquinas virtuales
        call(["sudo", "virsh", "start", self.name])
        #Abrimos terminal nuevo para cada MV
        os.system("xterm -rv -sb -rightbar -fa monospace -fs 10 -title '" + self.nombre + "' -e 'sudo virsh console "+ self.nombre + "' &")
        
    
    def show_console_vm(self):
        log.debug(f'Showing console of VM {self.name}')
        # Comando para mostrar consola de VM
    
    def stop_vm(self):
        log.debug(f'Stopping VM {self.name}')
        # Comando para detener VM
    
    def destroy_vm(self):
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