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

netmask = "255.255.255.0"


def edit_xml (vm):
    #Se obtiene el directorio de trabajo
    cwd = os.getcwd()  #método de OS que devuelve el Current Working Directory
    path = cwd + "/" + vm
    
    #Se importa el .xml de la máquina pasada como parámetro utilizando métodos de la librería LXML
    tree = etree.parse(path + ".xml")
    root = tree.getroot()
    
    #Se define el nombre de la MV
    name = root.find("name")
    name.text = vm
    
    #Se define el nombre de la imagen, cambiando la ruta del source de la imagen (disk) al qcow2 correspondiente a la maquina pasada como parametro
    sourceFile = root.find("./devices/disk/source")
    sourceFile.set("file", path + ".qcow2")
    
    #Se definen los bridges, modificando el XML con los bridges correspondientes a la maquina parámetro
    bridge = root.find("./devices/interface/source")
    bridge.set("bridge", bridges[vm][0])  #se cambia el valor de la etiqueta <source bridge> por la LAN (el bridge) correspondiente a la máquina pasada como parametro
    
    with open(path + ".xml" ,"w") as xml :
        xml.write(etree.tounicode(root, pretty_print=True))  #Se escribe el XML modificado en el archivo correspondiente a la máquina pasada como parámetro
    
    #Lo hacemos para lb ya que esta en 2 LANs distintas
    if vm == "lb" :
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

def config_network(vm):
    cwd = os.getcwd() #configuramos etc/hostname (modificando los ficheros)
    path = cwd + "/" + vm
    
    with open("hostname", "w") as hostname: 
        hostname.write(vm + "\n")  

    call(["sudo", "virt-copy-in", "-a", vm + ".qcow2", "hostname", "/etc"])#modificamos etc/hostname
    call(["rm", "-f", "hostname"])

    call(["sudo", "virt-edit", "-a", f"{vm}.qcow2", "/etc/hosts","-e", f"s/127.0.1.1.*/127.0.1.1 {vm}/"])#modificamos etc/hosts
    if vm == "lb":
        call(["sudo", "virt-edit", "-a", f"lb.qcow2", "/etc/network/interfaces","-e", f"$auto eth0\\niface eth0 inet static\\n    address 10.1.1.1\\n    netmask 255.255.255.0\\n" f"auto eth1\\niface eth1 inet static\\n    address 10.1.2.1\\n    netmask 255.255.255.0"])#modificamos etc/network/interfaces $$$$$$$$????????
        #call(["sudo", "virt-edit", "-a", f"{vm}.qcow2", "/etc/network/interfaces","-e", f"$auto eth1 \\n iface eth1 inet static \\n address 10.1.2.1 \\n netmask 255.255.255.0"])#modificamos etc/network/interfaces
        call(["sudo", "virt-edit", "-a", "lb.qcow2", "/etc/sysctl.conf", "-e", "'$net.ipv4.ip_forward = 1'"])
    else:
        call(["sudo", "virt-edit", "-a", f"{vm}.qcow2", "/etc/network/interfaces","-e", f"$auto eth0 \\n iface eth0 inet static \\n address {network[vm][0]}\\n netmask 255.255.255.0 \\n  gateway {network[vm][1]}"])#modificamos etc/network/interfaces

        
        

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
        log.debug(f'Mostrando consola de maquina virtual {self.name}')
        # Comando para mostrar consola de VM
    
    def stop_vm(self):
        log.debug(f'Apagando VM {self.name}')
        subprocess.call(["sudo", "virsh", "shutdown", self.name])
        log.info(f"Se ha detenido VM {self.name}")

    
    def destroy_vm(self):
        log.debug(f'Destruyendo VM {self.name}')
        subprocess.call(["sudo", "virsh", "destroy", self.name])
        subprocess.call(["sudo", "virsh", "undefine", self.name])
        os.remove(f"{self.name}.qcow2")
        os.remove(f"{self.name}.xml")
        log.info(f"Se ha destruido VM {self.name}")


class RED:
    def __init__(self, name):
        self.name = name
        log.debug(f'Inicializando Network {name}')
        
    def create_net(self):
        log.debug(f'Creando la red {self.name}')
        call(["sudo", "ovs-vsctl", "add-br", self.name])
        log.debug(f"Bridge {self.name} creado con éxito.")
    
    def destroy_net(self):
        log.debug(f'Destruyendo la red {self.name}')
        call(["sudo", "ovs-vsctl", "del-br", self.name])
        log.debug(f"Bridge {self.name} eliminado con éxito.")