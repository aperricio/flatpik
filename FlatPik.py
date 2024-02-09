from PyQt5 import QtGui
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread, Qt, QMetaObject, QRunnable, QThreadPool, Q_ARG
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QApplication, QGridLayout, QWidget, QMessageBox
from modules.assets import css, javascript
import subprocess, threading, requests, os
import webbrowser


app = QApplication(["FlatPik"])
icon = QtGui.QIcon()
icon.addPixmap(QtGui.QPixmap("img/FlatPik.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
app.setWindowIcon(icon)


class BuscarApp(QObject):
    def __init__(self):
        super().__init__()
        self.buscarApp("")

    @pyqtSlot(str)
    def buscarApp(self, busqueda):
        miReq = requests.post(url='https://flathub.org/api/v2/search', json={'query': busqueda})
        resultados_aarch64 = [resultado for resultado in miReq.json()['hits'] if 'aarch64' in resultado.get('arches', [])]

        if busqueda == "":
            contenedor_resultados = '<h2 id="h2_busqueda">Popular apps</h2>'
        else:
            contenedor_resultados = '<h2 id="h2_busqueda">' + str(len(resultados_aarch64)) + ' results for "' + busqueda + '"</h2>'
        contenedor_resultados += '<section id="resultados">'

        if len(resultados_aarch64) > 0:
            for resultado in resultados_aarch64:
                nombre = resultado['name'] 
                icono = resultado['icon'] 
                descripcion_corta = resultado['summary']
                app_id = resultado['app_id']
                pagina_web = resultado['verification_website'] if resultado['verification_website'] != None else "https://flathub.org/apps/" + app_id
                verificada = resultado['verification_verified']
                marca_verificacion = ' <span class="uve">&#10003;</span><span class="verificada">erified</span>' if verificada == 'true' else ''
                try:
                    contenedor_resultados += '<article><img src="' + icono + '"><h2 onclick="abrir_web(\'' + pagina_web + '\')">' + nombre + marca_verificacion + '</h2><button class="instalar" onclick="instalar_paquete(\'' + app_id + '\', \'' + nombre +'\')">&#10225;</button><p>' + descripcion_corta + '</p></article>'
                except TypeError:
                    """Error que no debería saltar al realizar algunas búsquedas"""
        else:
            contenedor_resultados += '<article style="text-align:center"><h3 style="margin-top:70px">No aarch64 matches for that query</h3></article>'

        contenedor_resultados += "</section>"

        boton_soporte = """<button id="actualizar" onclick="actualizar_todo()">&#10227;</button><span id="tipactualizartodo">Update all</span>""" if os.path.exists("/usr/bin/flatpak") else '<button id="soporte" onclick="activar_soporte()">&#9881;</button><span id="tipsoporte">Add flatpak support</span>'
        global html
        html = css + """
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<body> """ + boton_soporte + """
<button onclick="funcionArriba()" id="botonArriba">&#8593;</button>
<header id="h1_flatpik"><h1>FlatPik</h1></header>
<section id="buscar"><input type="text" id="busqueda"><button id="enviar_busqueda" onclick="enviar_busqueda()">&#8618;</button></section>
""" + contenedor_resultados + javascript + '</body>'


        view.page().setHtml(html)    


class ActivarSoporteWorker(QObject):
    activarSoporteTerminado = pyqtSignal(int)

    @pyqtSlot()
    def ejecutar_activacion(self):
        proceso = subprocess.Popen("sudo apt install flatpak && flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo", shell=True)
        proceso.wait()

        self.activarSoporteTerminado.emit(proceso.returncode)

class ActivarSoporte(QObject):
    @pyqtSlot()
    def activar_soporte(self):
        self.hilo_activacion = QThread()
        self.worker_activacion = ActivarSoporteWorker()
        self.worker_activacion.moveToThread(self.hilo_activacion)

        self.worker_activacion.activarSoporteTerminado.connect(self.activacion_terminada)

        self.hilo_activacion.started.connect(self.worker_activacion.ejecutar_activacion)
        self.hilo_activacion.finished.connect(self.worker_activacion.deleteLater)
        self.hilo_activacion.finished.connect(self.hilo_activacion.deleteLater)

        self.hilo_activacion.start()

    def activacion_terminada(self, return_code):
        if return_code == 0:
            QMetaObject.invokeMethod(self, "mostrar_activacion_exito", Qt.QueuedConnection)
        elif return_code ==1:
            QMetaObject.invokeMethod(self, "mostrar_actualizacion_error", Qt.QueuedConnection)
        elif return_code == 255:
            print("Parada manual")

    @pyqtSlot()
    def mostrar_activacion_exito(self):
        mensaje_informacion = QMessageBox()
        mensaje_informacion.setIcon(QMessageBox.Information)
        mensaje_informacion.setWindowTitle("Add flatpak support")
        mensaje_informacion.setText('<b>Success</b>')
        mensaje_informacion.setInformativeText("<p style=\"margin-right:25px\">flatpak package installed and Flathub PPA added. You can install flatpak apps now.<br><br>Reboot required.")
        mensaje_informacion.exec_()
        BuscarApp.buscarApp(self, "")
    @pyqtSlot()
    def mostrar_actualizacion_error(self):
        mensaje_informacion = QMessageBox()
        mensaje_informacion.setIcon(QMessageBox.Information)
        mensaje_informacion.setWindowTitle("Add flatpak support")
        mensaje_informacion.setText('<b>Error</b>')
        mensaje_informacion.setInformativeText("<p style=\"margin-right:25px\">An error occurred during installation. Please try again.")
        mensaje_informacion.exec_()

class ActualizarTodoWorker(QObject):
    actualizarTerminado = pyqtSignal(int)

    @pyqtSlot()
    def ejecutar_actualizacion(self):
        proceso = subprocess.Popen(["flatpak", "update", "-y"])
        proceso.wait()

        self.actualizarTerminado.emit(proceso.returncode)


class ActualizarTodo(QObject):
    #mostrarVentanaEmergente = pyqtSignal()

    @pyqtSlot()
    def actualizar_todo(self):
        self.hilo_actualizacion = QThread()
        self.worker_actualizacion = ActualizarTodoWorker()
        self.worker_actualizacion.moveToThread(self.hilo_actualizacion)

        self.worker_actualizacion.actualizarTerminado.connect(self.actualizacion_terminada)

        self.hilo_actualizacion.started.connect(self.worker_actualizacion.ejecutar_actualizacion)
        self.hilo_actualizacion.finished.connect(self.worker_actualizacion.deleteLater)
        self.hilo_actualizacion.finished.connect(self.hilo_actualizacion.deleteLater)

        self.hilo_actualizacion.start()

    def actualizacion_terminada(self, return_code):
        if return_code == 0:
            QMetaObject.invokeMethod(self, "mostrar_actualizacion_exito", Qt.QueuedConnection)
            print("Éxito")
        elif return_code == 1:  # Error
            QMetaObject.invokeMethod(self, "mostrar_actualizacion_error", Qt.QueuedConnection)
            print("Error")
        elif return_code == 255:  # Parada manual
            print("Parada manual")

    @pyqtSlot()
    def mostrar_actualizacion_exito(self):
        mensaje_informacion = QMessageBox()
        mensaje_informacion.setIcon(QMessageBox.Information)
        mensaje_informacion.setWindowTitle("Update all")
        mensaje_informacion.setText('<b>Success</b>')
        mensaje_informacion.setInformativeText("<p style=\"margin-right:25px\">All flatpaks and runtimes are up to date.")
        mensaje_informacion.exec_()

    @pyqtSlot()
    def mostrar_actualizacion_error(self):
        mensaje_informacion = QMessageBox()
        mensaje_informacion.setIcon(QMessageBox.Information)
        mensaje_informacion.setWindowTitle("Update all")
        mensaje_informacion.setText('<b>Error</b>')
        mensaje_informacion.setInformativeText("<p style=\"margin-right:25px\">An error occurred during the update. Please try again.")
        mensaje_informacion.exec_()



class InstalarAppWorker(QThread):
    instalarAppTerminado = pyqtSignal(int, str)

    def __init__(self, id_app, nombre_app):
        super().__init__()
        self.id_app = id_app
        self.nombre_app = nombre_app

    def run(self):
        proceso = subprocess.Popen(["flatpak", "install", "flathub", self.id_app, "-y"])
        proceso.wait()
        self.instalarAppTerminado.emit(proceso.returncode, self.nombre_app)

class InstalarApp(QObject):
    def __init__(self):
        super().__init__()
        self.worker_instalacion = None

    @pyqtSlot(str, str)
    def instalar_paquete(self, id_app, nombre_app):
        self.worker_instalacion = InstalarAppWorker(id_app, nombre_app)
        self.worker_instalacion.instalarAppTerminado.connect(self.instalacion_terminada)
        self.worker_instalacion.start()

    def instalacion_terminada(self, return_code, nombre_app):
        if return_code == 0:
            QMetaObject.invokeMethod(self, "mostrar_instalacion_exito", Qt.QueuedConnection, Q_ARG(str, nombre_app))
            print("Éxito")
            print("Nombre de la aplicación:", nombre_app)
        elif return_code == 1:
            QMetaObject.invokeMethod(self, "mostrar_instalacion_error", Qt.QueuedConnection, Q_ARG(str, nombre_app))
            print("Error")
        elif return_code == 255:
            print("Parada manual")

    @pyqtSlot(str)
    def mostrar_instalacion_exito(self, nombre_app):
        mensaje_informacion = QMessageBox()
        mensaje_informacion.setIcon(QMessageBox.Information)
        mensaje_informacion.setWindowTitle("Install app")
        mensaje_informacion.setText('<b>Success</b>')
        mensaje_informacion.setInformativeText(f"<p style=\"margin-right:25px\">{nombre_app} app is now installed.")
        mensaje_informacion.exec_()

    @pyqtSlot(str)
    def mostrar_instalacion_error(self, nombre_app):
        mensaje_informacion = QMessageBox()
        mensaje_informacion.setIcon(QMessageBox.Information)
        mensaje_informacion.setWindowTitle("Install app")
        mensaje_informacion.setText('<b>Error</b>')
        mensaje_informacion.setInformativeText(f"<p style=\"margin-right:25px\">Failed to install {nombre_app} app. Try again, please.")
        mensaje_informacion.exec_()



class PaginaWeb(QObject):
    @pyqtSlot(str)
    def abrir_pagina_web(self, url):
        try: 
            webbrowser.open(url)
        except:
            try: 
                subprocess.Popen(["chromium-browser", url])
            except FileNotFoundError:
                subprocess.Popen(["firefox", url])


visor = QWidget()

layout = QGridLayout()
layout.setContentsMargins(0, 0, 0, 0)
visor.setLayout(layout)

view = QWebEngineView()
page = QWebEnginePage(view)
channel = QWebChannel()
page.setWebChannel(channel)
botonActivarSoporte = ActivarSoporte()
channel.registerObject("botonInstalarFlatpak", botonActivarSoporte)
botonBuscarApp = BuscarApp()
channel.registerObject("botonBuscar", botonBuscarApp)
botonInstalarApp = InstalarApp()
channel.registerObject("botonInstalarPaquete", botonInstalarApp)
botonAbrirWeb = PaginaWeb()
channel.registerObject("botonAbrirWeb", botonAbrirWeb)
botonActualizarTodo = ActualizarTodo()
channel.registerObject("botonActualizarTodo", botonActualizarTodo)
view.setPage(page)
view.page().setHtml(html)                    

layout.addWidget(view, 0, 0, 1, 1)
visor.setMinimumSize(400, 500)
visor.setGeometry(0, 0, 1256, 720)

visor.show()
app.exec_()
