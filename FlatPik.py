#!/usr/bin/env python3
from PyQt5 import QtGui
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QApplication, QMessageBox, QGridLayout, QWidget
from modules.assets import css, javascript
import subprocess, threading, requests


app = QApplication(["FlatPik"])
icon = QtGui.QIcon()
icon.addPixmap(QtGui.QPixmap("img/FlatPik.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
app.setWindowIcon(icon)

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

        #global contenedor_resultados
        if busqueda == "":
            contenedor_resultados = '<h2 id="h2_busqueda">Popular apps</h2>'
        elif numero_resultados >= 0:
            contenedor_resultados = '<h2 id="h2_busqueda">' + str(numero_resultados) + ' results</h2>'
        """ else:
            contenedor_resultados = "" """
        contenedor_resultados += '<section id="resultados">'

        if numero_resultados > 0:
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
            contenedor_resultados += '<article style="text-align:center"><h3 style="margin-top:70px">No aarch64 match for that query</h3></article>'

        contenedor_resultados += "</section>"

        global html
        html = css + """
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<body>
<button id="soporte" onclick="activar_soporte()">&#9881;</button><span id="tipsoporte" style=";">Add flatpak support</span>
<header id="h1_flatpik"><h1>FlatPik</h1></header>
<section id="buscar"><input type="text" id="busqueda"><button id="enviar_busqueda" onclick="enviar_busqueda()">&#8618;</button></section>
""" + contenedor_resultados + javascript + "</body>"


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
