#!/usr/bin/env python3
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QApplication, QMessageBox, QGridLayout, QWidget
import subprocess,threading
import requests


app = QApplication(["FlatPik"])
css = """<style>

    body {
        background-color: #1D1D1D;
        color: #CD2355;
    }

    #h1_flatpik {
        color: #CD2355;
        text-align: center;
        font-size: 1.6rem;
        transition: 1s;
        position: fixed;
        top: 0;
        left:0;
        z-index: 112;
        background-color: #111;
        margin: 0;
        width: 100vw;
    }

    #h1_flatpik + * {
        margin-top:180px;
    }

    #h2_busqueda {
        text-align: center;
        margin-bottom: -20px
    }

    ::-webkit-scrollbar {
        width: 0px;
    }

    #soporte:focus, #buscar input:focus {
        outline: none;
    }

    #buscar button:focus, .instalar:focus {
        outline: none;
        box-shadow: 1px 1px 3px grey
    }


    #soporte {
        background-color: #1f1f1f;
        border: 2px solid #CD2355;
        color: #CD2355;
        font-size: 1.7rem;
        transition: .2s;
        border-radius: 5px;
        position: fixed;
        z-index:111;
        padding: 3px 7px;
        left: 10px;
        bottom: 10px;
    }


    #soporte:hover, #buscar button:hover, .instalar:hover {
        background-color: #CD2355;
        border: 2px solid #CD2355;
        color: #1f1f1f;
        cursor: pointer
    }

    #soporte:hover + #tipsoporte {
        opacity:1;
    }

    #tipsoporte {
        color: #CD2355;
        font-size: 1.2rem;
        position: fixed;
        opacity: 0;
        transition: .3s;
        text-shadow: 2px 2px 1px black, 1px 1px 1px black, 3px 3px 1px black;
        z-index:111;
    }

    #tipsoporte {
        left: 60px;
        bottom: 18px;        
    }

    #buscar {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }

    #buscar input {
        margin: 0 10px;
        text-align: center;
        font-size: 1.1rem;
        background-color: #555;
        border: 2px solid #111;
        border-radius: 5px
    }

    #buscar button {
        background-color: #1f1f1f;
        border: 2px solid #CD2355;
        color: #CD2355;
        font-size: 1.2rem;
        transition: .2s;
        border-radius: 5px;
        z-index:111;
        padding: 3px 7px;
    }

    #resultados {
        margin: 50px;
        display: flex;
        flex-wrap: wrap;
        justify-content: center
    }

    #resultados article {
        width: 350px;
        height: 170px;
        display: inline-block;
        position: relative;
        margin: 3px;
        border: 2px solid grey;
        padding: 0 10px;
        border-radius: 8px;
        overflow: scroll;
        background-color: #161616
    }

    #resultados h2 {
        font-size: 1.2rem;
        padding: 0;
    }

    #resultados article img {
        height: 50px;
        float: right;
        position: relative;
        top: 10px;
    }

    #resultados p {
        padding-top: 10px
    }

    .instalar {
        background-color: #1f1f1f;
        border: 2px solid #CD2355;
        color: #CD2355;
        font-size: 1.2rem;
        transition: .2s;
        border-radius: 5px;
        z-index:111;
        padding: 3px 7px;
        margin: 25px 7px 0;
        float: right;
    }

    .verificada {
        font-size: 0.85rem;
        transition: .5s;
        opacity: 0;
        position: relative;
        right: 5px;
        bottom: 1.5px;
    }

    .uve {
        font-size: 1.5rem
    }
    .uve:hover + .verificada {
        opacity: 1
    }

</style>"""

html=""

class Buscar(QObject):
    def __init__(self):
        super().__init__()
        self.buscar("") # Se ejecuta al iniciar sin nada (muestra el apartado de "Populares")
    @pyqtSlot(str)  
    def buscar(self, busqueda):
        miReq = requests.post(url='https://flathub.org/api/v2/search', json={'query': busqueda})

        resultados_aarch64 = [resultado for resultado in miReq.json()['hits'] if 'aarch64' in resultado.get('arches', [])]

        numero_resultados = len(resultados_aarch64)

        global contenedor_resultados
        if busqueda == "":
            contenedor_resultados = '<h2 id="h2_busqueda">Popular apps</h2>'
        elif len(resultados_aarch64) > 0:
            contenedor_resultados = '<h2 id="h2_busqueda">' + str(numero_resultados) + ' results</h2>'
        else:
            contenedor_resultados = ""
        contenedor_resultados += '<section id="resultados">'

        if len(miReq.json()['hits']) > 0:
            for resultado in miReq.json()['hits']:
                if "aarch64" in resultado['arches']:
                    nombre = resultado['name'] 
                    icono = resultado['icon'] 
                    descripcion_corta = resultado['summary']
                    app_id = resultado['app_id']
                    verificada = resultado['verification_verified']
                    marca_verificacion = ' <span class="uve">&#10003;</span><span class="verificada">erificada</span>' if verificada == 'true' else ''
                    contenedor_resultados += '<article><img src="' + icono + '"><h2>' + nombre + marca_verificacion + '</h2><button class="instalar" onclick="instalar_paquete(\'' + app_id + '\')">&#10225;</button><p>' + descripcion_corta + '</p></article>'
        else:
            contenedor_resultados += "<article><h2>0 Results</h2><p>No match for that query</p></article>"

        contenedor_resultados += "</section>"

        global html
        html = css + """
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<body>
<button id="soporte" onclick="activar_soporte()">&#9881;</button><span id="tipsoporte" style=";">Add flatpak support</span>
<header id="h1_flatpik"><h1>FlatPik</h1></header>
<section id="buscar"><input type="text" id="busqueda"><button id="enviar_busqueda" onclick="enviar_busqueda()">&#8618;</button></section>
""" + contenedor_resultados + """
<script>
     setTimeout(function() {
        document.getElementById("busqueda").focus();
    }, 100); 

    let objetoInstalarFlatpak = null;
    let objetoBuscar = null;
    let objetoInstalarPaquete = null;
    new QWebChannel(qt.webChannelTransport, function (channel) {
        objetoInstalarFlatpak = channel.objects.botonInstalarFlatpak;
        objetoBuscar = channel.objects.botonBuscar;
        objetoInstalarPaquete = channel.objects.botonInstalarPaquete;
    });

    function activar_soporte() {
        objetoInstalarFlatpak.activar_soporte();
    }

    function enviar_busqueda() {
        let busqueda = document.getElementById('busqueda').value;
        objetoBuscar.buscar(busqueda)
    }


    function instalar_paquete(id_app) {
        objetoInstalarPaquete.instalar_paquete(id_app);
    }

    document.getElementById("busqueda").addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();  // Evitar que el Enter envíe el formulario
            document.getElementById("enviar_busqueda").click();
        }
    });


    window.onscroll = function() {scrollFunction()};

    function scrollFunction() {
        if (document.body.scrollTop > 120) {
            document.getElementById("h1_flatpik").style.fontSize = "0.45rem";
        } else {
            document.getElementById("h1_flatpik").style.fontSize = "1.6rem";
        }
    }

</script></body>""" 


        view.page().setHtml(html)    



class Soporte(QObject):
    @pyqtSlot()
    def activar_soporte(self):
        threading.Thread(target=self.ejecutar_activacion).start()

    def ejecutar_activacion(self):
        proceso = subprocess.Popen("apt install flatpak && flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo", shell=True)
        proceso.wait()

        if proceso.returncode == 0:
            print("Éxito")
        elif proceso.returncode == 1: #Error
            print("Error")
        elif proceso.returncode == 255: #Parada manual
            print("Parada manual")


class Instalar(QObject):
    @pyqtSlot(str)
    def instalar_paquete(self, id_app):
        threading.Thread(target=lambda: self.ejecutar_instalacion(id_app)).start()
    
    def ejecutar_instalacion(self, id_app):
        proceso= subprocess.Popen(["flatpak", "install", "flathub",  id_app, "-y"])
        proceso.wait()

        if proceso.returncode == 0:
            print("Éxito")
        elif proceso.returncode == 1: #Error
            print("Error")
        elif proceso.returncode == 255: #Parada manual
            print("Parada manual")

# Crear el objeto QWidget para la ventana principal
visor = QWidget()

# Configurar el layout de la ventana principal
layout = QGridLayout()
layout.setContentsMargins(0, 0, 0, 0)
visor.setLayout(layout)

# Crear el objeto QWebEngineView
view = QWebEngineView()
page = QWebEnginePage(view)
channel = QWebChannel()
page.setWebChannel(channel)
botonActivarSoporte = Soporte()
channel.registerObject("botonInstalarFlatpak", botonActivarSoporte)
botonBuscar = Buscar()
channel.registerObject("botonBuscar", botonBuscar)
botonInstalarPaquete = Instalar()
channel.registerObject("botonInstalarPaquete", botonInstalarPaquete)
view.setPage(page)
view.page().setHtml(html)                    

# Agregar el QWebEngineView al layout de la ventana principal
layout.addWidget(view, 0, 0, 1, 1)

# Mostrar la ventana principal
visor.setMinimumSize(400, 500)
visor.setGeometry(0, 0, 1256, 700)
#visor.showMaximized()

visor.show()
app.exec_()
