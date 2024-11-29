import logging, os
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
    #Creamos un arbol estructurado con el XML de la máquina pasada como parámetro
    tree = etree.parse(path + ".xml")
    #Se obtiene la raíz del árbol con la que podemos acceder a los elementos fijos
    root = tree.getroot()
    
    #Se define el nombre de la MV
    name = root.find("name")
    if name is not None:
        name.text = vm
    
    #Se define el nombre de la imagen, cambiando la ruta del source de la imagen (disk) al qcow2 correspondiente a la maquina pasada como parametro
    sourceFile = root.find("./devices/disk/source")
    if sourceFile is not None:
        sourceFile.set("file", path + ".qcow2")
    
    #Se definen los bridges, modificando el XML con los bridges correspondientes a la maquina parámetro
    bridge = root.find("./devices/interface/source")
    if bridge is not None:
        bridge.set("bridge", bridges[vm][0])  #se cambia el valor de la etiqueta <source bridge> por la LAN (el bridge) correspondiente a la máquina pasada como parametro
    
    #Con esto abrimos archivo "xml" en modo escritura, y escribimos en él el XML modificado (si no existe se crea)
    with open(path + ".xml" ,"w") as xml :
        xml.write(etree.tounicode(root, pretty_print=True))  #Se escribe el XML modificado en el archivo correspondiente a la máquina pasada como parámetro
    
    #Lo hacemos para lb ya que esta en 2 LANs distintas
    if vm == "lb" :
        fcopy = open(path + ".xml",'r')   #fin es el XML correspondiente a lb, en modo solo lectura
        ftemporal = open("temporal.xml",'w')  #fout es un XML temporal abierto en modo escritura
        for linea in fcopy:
            if "</interface>" in linea:
                ftemporal.write("</interface>\n <interface type='bridge'>\n <source bridge='"+"LAN2"+"'/>\n <model type='virtio'/>\n <virtualport type='openvswitch'\n </interface>\n")
        #si el XML de lb contiene un interface (que lo va a contener, ya que previamente se le habrá añadido el bridge LAN1), se le añade al XML temporal otro bridge: LAN2
        else:
            ftemporal.write(linea)
        fcopy.close()
        ftemporal.close()
        call(["cp","./temporal.xml", path + ".xml"])  #sustituimos es XML por el temporal, que es el que contiene las dos LAN
        call(["rm", "-f", "./temporal.xml"])

def config_network(vm):
    cwd = os.getcwd()
    path = cwd + "/" + vm
    
    with open("hostname", "w") as hostname:
        hostname.write(vm + "\n")
        
    call(["sudo", "virt-copy-in", "-a", vm + ".qcow2", "hostname", "/etc"])
    call(["rm", "-f", "hostname"])
    
    #Configuracion del host, que asigna nombres de host a direcciones IP
    #Asigna la direccion IP local a la maquina pasada como parametr
    call("sudo virt-edit -a " + vm + ".qcow2 /etc/hosts -e 's/127.0.1.1.*/127.0.1.1 " + vm + "/'", shell=True) #cambiarlo
    
    with open("interfaces", "w") as interfaces:
        if vm == "lb":
            #Añade a interfaces sus dos interfaces correspondientes a LAN1 y LAN2 al ser lb
            interfaces.write("auto lo\niface lo inet loopback\n\nauto eth0\niface eth0 inet static\n  address 10.11.1.1\n netmask" + netmask + "\nauto eth1\niface eth1 inet static\n  address 10.11.2.1\n netmask " + netmask)
        else:
            #Añade la direccion IP correspondiente a la maquina, y la direccion del LB en gateway
            interfaces.write("auto lo \niface lo inet loopback \n\nauto eth0 \niface eth0 inet static \naddress " + network[vm][0] + " \nnetmask" + netmask + "\ngateway " + network[vm][1])
        
    call(["sudo", "virt-copy-in", "-a", vm + ".qcow2", "interfaces", "/etc/network"])
    call(["rm", "-f", "interfaces"])
    #Habilitamos forwarding IPv4 para que lb funcione como router al arrancar
    if vm == "lb":
        call("sudo virt-edit -a lb.qcow2 /etc/sysctl.conf -e 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/'", shell=True)
        
        

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
        #Apagamos las maquinas virtuales
        call(["sudo", "virsh", "shutdown", self.name])
        log.info(f"Se ha detenido VM {self.name}")

    
    def destroy_vm(self):
        log.debug(f'Destruyendo VM {self.name}')
        #Destruimos las maquinas virtuales
        call(["sudo", "virsh", "destroy", self.name])
        #Desdefinimos las maquinas virtuales
        call(["sudo", "virsh", "undefine", self.name])
        #Eliminamos los archivos de configuración de las MVs
        os.remove(f"{self.name}.qcow2")
        os.remove(f"{self.name}.xml")
        log.info(f"Se ha destruido VM {self.name}")


class RED:
    def __init__(self, name):
        self.name = name
        log.debug(f'Inicializando Network {name}')
        
    def create_red(self):
        log.debug(f'Creando la red {self.name}')
        call(["sudo", "ovs-vsctl", "add-br", self.name])
        log.debug(f"Bridge {self.name} creado con éxito.")
    
    def destroy_red(self):
        log.debug(f'Destruyendo la red {self.name}')
        call(["sudo", "ovs-vsctl", "del-br", self.name])
        log.debug(f"Bridge {self.name} eliminado con éxito.")