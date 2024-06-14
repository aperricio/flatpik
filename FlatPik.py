from PyQt6 import QtGui
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QThread, Qt, QMetaObject, Q_ARG
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QGridLayout, QWidget, QMessageBox, QStatusBar
from modules.assets import css, javascript
import subprocess, requests, os
import webbrowser

app = QApplication(["FlatPik"])
icon = QtGui.QIcon()
icon.addPixmap(QPixmap("img/FlatPik.png"))
app.setWindowIcon(icon)

conf = os.path.expanduser("~/.config/FlatPik/claro.txt")
conf_dir = os.path.expanduser("~/.config/FlatPik")

def comprobar_tema():
    global tema
    global sol_o_luna
    if os.path.exists(conf):
        sol_o_luna = "☾"
        tema = """
    :root {
        --fondo: #EEE;
        --fondo2: #CCC;
        --fondo3: #888;
        --fondo4: #A5A5A5;
        --fondoBusqueda: #151515;
        --fondoArticle: #B5B5B5;
        --texto: #CD2355;
    }
    """
    else:
        sol_o_luna = "☼"
        tema = """
    :root {
        --fondo: #1D1D1D;
        --fondo2: #111;
        --fondo3: #1f1f1f;
        --fondo4: #555;
        --fondoBusqueda: #151515;
        --fondoArticle: #161616;
        --texto: #CD2355;
    }
    """

comprobar_tema()

class BuscarApp(QObject):
    def __init__(self):
        super().__init__()
        self.buscarApp("")

    @pyqtSlot(str)
    def buscarApp(self, busqueda):
        comprobar_tema()
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
                if os.path.exists("/var/lib/flatpak/app/" + app_id):
                    boton_instalar_desinstalar = '<button class="desinstalar" onclick="desinstalar_paquete(\'' + app_id + '\', \'' + nombre +'\')">✗</button>'
                else: 
                    boton_instalar_desinstalar = '<button class="instalar" onclick="instalar_paquete(\'' + app_id + '\', \'' + nombre +'\')">&#10225;</button>'
                pagina_web = resultado['verification_website'] if resultado['verification_website'] != None else "https://flathub.org/apps/" + app_id
                verificada = resultado['verification_verified']
                marca_verificacion = ' <span class="uve">&#10003;</span><span class="verificada">erified</span>' if verificada == 'true' else ''
                try:
                    contenedor_resultados += '<article><img src="' + icono + '"><h2 onclick="abrir_web(\'' + pagina_web + '\')">' + nombre + marca_verificacion + '</h2>' + boton_instalar_desinstalar + '<p>' + descripcion_corta + '</p></article>'
                except TypeError:
                    """Error que no debería saltar al realizar algunas búsquedas"""
        else:
            contenedor_resultados += '<article style="text-align:center"><h3 style="margin-top:70px">No aarch64 matches for that query</h3></article>'

        contenedor_resultados += "</section>"

        boton_soporte = """<button id="actualizar" onclick="actualizar_todo()">&#10227;</button><span id="tipactualizartodo">Update all</span>""" if os.path.exists("/usr/bin/flatpak") else '<button id="soporte" onclick="activar_soporte()">&#9881;</button><span id="tipsoporte">Add flatpak support</span>'
        global html
        html = "<style>" + tema + css + """
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<body> """ + boton_soporte + """
<button onclick="funcionArriba()" id="botonArriba">&#8593;</button>
<header id="h1_flatpik"><h1>FlatPik</h1></header>
<section id="buscar"><input type="text" id="busqueda" value=""" + "\""+busqueda+"\"" +"""><button id="enviar_busqueda" onclick="enviar_busqueda()">&#8618;</button></section>
<span id="interruptor" onclick="cambiarTema()">""" + sol_o_luna +"</span>" + contenedor_resultados + javascript + '</body>'


        view.page().setHtml(html)    


class ActivarSoporteWorker(QObject):
    activarSoporteTerminado = pyqtSignal(int)

    @pyqtSlot()
    def ejecutar_activacion(self):
        layout.addWidget(status_bar, 1, 0, 1, -1)
        status_bar.showMessage("Adding flatpak support. Please, wait.")
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
            QMetaObject.invokeMethod(self, "mostrar_activacion_exito", Qt.ConnectionType.QueuedConnection)
        elif return_code ==1:
            QMetaObject.invokeMethod(self, "mostrar_actualizacion_error", Qt.ConnectionType.QueuedConnection)
        elif return_code == 255:
            print("Parada manual")

    @pyqtSlot()
    def mostrar_activacion_exito(self):
        mensaje_informacion = QMessageBox()
        mensaje_informacion.setIcon(QMessageBox.Icon.Information)
        mensaje_informacion.setWindowTitle("Add flatpak support")
        mensaje_informacion.setText('<b>Success</b>')
        mensaje_informacion.setInformativeText("<p style=\"margin-right:25px\">flatpak package installed and Flathub PPA added. You can install flatpak apps now.<br><br>Reboot required.")
        layout.addWidget(status_bar, 1, 0, 0, -1)
        mensaje_informacion.exec()
        BuscarApp.buscarApp(self, "")
    @pyqtSlot()
    def mostrar_actualizacion_error(self):
        mensaje_informacion = QMessageBox()
        mensaje_informacion.setIcon(QMessageBox.Icon.Information)
        mensaje_informacion.setWindowTitle("Add flatpak support")
        mensaje_informacion.setText('<b>Error</b>')
        mensaje_informacion.setInformativeText("<p style=\"margin-right:25px\">An error occurred during installation. Please try again.")
        mensaje_informacion.exec()

class ActualizarTodoWorker(QObject):
    actualizarTerminado = pyqtSignal(int)

    @pyqtSlot()
    def ejecutar_actualizacion(self):
        layout.addWidget(status_bar, 1, 0, 1, -1)
        status_bar.showMessage("Updating. Please, wait.")
        proceso = subprocess.Popen(["flatpak", "update", "-y"])
        proceso.wait()

        self.actualizarTerminado.emit(proceso.returncode)


class ActualizarTodo(QObject):
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
            QMetaObject.invokeMethod(self, "mostrar_actualizacion_exito", Qt.ConnectionType.QueuedConnection)
            print("Éxito")
        elif return_code == 1:  # Error
            QMetaObject.invokeMethod(self, "mostrar_actualizacion_error", Qt.ConnectionType.QueuedConnection)
            print("Error")
        elif return_code == 255:  # Parada manual
            print("Parada manual")

    @pyqtSlot()
    def mostrar_actualizacion_exito(self):
        mensaje_informacion = QMessageBox()
        mensaje_informacion.setIcon(QMessageBox.Icon.Information)
        mensaje_informacion.setWindowTitle("Update all")
        mensaje_informacion.setText('<b>Success</b>')
        mensaje_informacion.setInformativeText("<p style=\"margin-right:25px\">All flatpaks and runtimes are up to date.")
        layout.addWidget(status_bar, 1, 0, 0, -1)
        mensaje_informacion.exec()

    @pyqtSlot()
    def mostrar_actualizacion_error(self):
        mensaje_informacion = QMessageBox()
        mensaje_informacion.setIcon(QMessageBox.Icon.Information)
        mensaje_informacion.setWindowTitle("Update all")
        mensaje_informacion.setText('<b>Error</b>')
        mensaje_informacion.setInformativeText("<p style=\"margin-right:25px\">An error occurred during the update. Please try again.")
        layout.addWidget(status_bar, 1, 0, 0, -1)
        mensaje_informacion.exec()


class InstalarAppWorker(QThread):
    instalarAppTerminado = pyqtSignal(int, str)

    def __init__(self, id_app, nombre_app):
        super().__init__()
        self.id_app = id_app
        self.nombre_app = nombre_app

    def run(self):
        layout.addWidget(status_bar, 1, 0, 1, -1)
        mensaje="Installing " + self.nombre_app + ". Please, wait."
        status_bar.showMessage(mensaje)
        proceso = subprocess.Popen(["flatpak", "install", "--system", "flathub", self.id_app, "-y"])
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
            QMetaObject.invokeMethod(self, "mostrar_instalacion_exito", Qt.ConnectionType.QueuedConnection, Q_ARG(str, nombre_app))
            print("Éxito")
            print("Nombre de la aplicación:", nombre_app)
        elif return_code == 1:
            QMetaObject.invokeMethod(self, "mostrar_instalacion_error", Qt.ConnectionType.QueuedConnection, Q_ARG(str, nombre_app))
            print("Error")
        elif return_code == 255:
            print("Parada manual")

    @pyqtSlot(str)
    def mostrar_instalacion_exito(self, nombre_app):
        mensaje_informacion = QMessageBox()
        mensaje_informacion.setIcon(QMessageBox.Icon.Information)
        mensaje_informacion.setWindowTitle("Install app")
        mensaje_informacion.setText('<b>Success</b>')
        mensaje_informacion.setInformativeText(f"<p style=\"margin-right:25px\">{nombre_app} app is now installed.")
        layout.addWidget(status_bar, 1, 0, 0, -1)
        mensaje_informacion.exec()

    @pyqtSlot(str)
    def mostrar_instalacion_error(self, nombre_app):
        mensaje_informacion = QMessageBox()
        mensaje_informacion.setIcon(QMessageBox.Icon.Information)
        mensaje_informacion.setWindowTitle("Install app")
        mensaje_informacion.setText('<b>Error</b>')
        mensaje_informacion.setInformativeText(f"<p style=\"margin-right:25px\">Failed to install {nombre_app} app. Try again, please.")
        layout.addWidget(status_bar, 1, 0, 0, -1)
        mensaje_informacion.exec()


class DesinstalarAppWorker(QThread):
    desinstalarAppTerminado = pyqtSignal(int, str)

    def __init__(self, id_app, nombre_app):
        super().__init__()
        self.id_app = id_app
        self.nombre_app = nombre_app

    def run(self):
        layout.addWidget(status_bar, 1, 0, 1, -1)
        mensaje="Uninstalling " + self.nombre_app + ". Please, wait."
        status_bar.showMessage(mensaje)
        proceso = subprocess.Popen(["flatpak", "uninstall", "--system", "flathub", self.id_app, "-y"])
        proceso.wait()
        self.desinstalarAppTerminado.emit(proceso.returncode, self.nombre_app)

class DesinstalarApp(QObject):
    def __init__(self):
        super().__init__()
        self.worker_desinstalacion = None

    @pyqtSlot(str, str)
    def desinstalar_paquete(self, id_app, nombre_app):
        self.worker_desinstalacion = DesinstalarAppWorker(id_app, nombre_app)
        self.worker_desinstalacion.desinstalarAppTerminado.connect(self.desinstalacion_terminada)
        self.worker_desinstalacion.start()

    def desinstalacion_terminada(self, return_code, nombre_app):
        if return_code == 0:
            QMetaObject.invokeMethod(self, "mostrar_desinstalacion_exito", Qt.ConnectionType.QueuedConnection, Q_ARG(str, nombre_app))
            print("Éxito")
            print("Nombre de la aplicación:", nombre_app)
        elif return_code == 1:
            QMetaObject.invokeMethod(self, "mostrar_desinstalacion_error", Qt.ConnectionType.QueuedConnection, Q_ARG(str, nombre_app))
            print("Error")
        elif return_code == 255:
            print("Parada manual")
        
        
        

    @pyqtSlot(str)
    def mostrar_desinstalacion_exito(self, nombre_app):
        mensaje_informacion = QMessageBox()
        mensaje_informacion.setIcon(QMessageBox.Icon.Information)
        mensaje_informacion.setWindowTitle("Uninstall app")
        mensaje_informacion.setText('<b>Success</b>')
        mensaje_informacion.setInformativeText(f"<p style=\"margin-right:25px\">{nombre_app} app is now uninstalled. Run \"flatpak uninstall --unused --delete-data -y\" to delete app configuration.")
        layout.addWidget(status_bar, 1, 0, 0, -1)
        mensaje_informacion.exec()

    @pyqtSlot(str)
    def mostrar_desinstalacion_error(self, nombre_app):
        mensaje_informacion = QMessageBox()
        mensaje_informacion.setIcon(QMessageBox.Icon.Information)
        mensaje_informacion.setWindowTitle("Uninstall app")
        mensaje_informacion.setText('<b>Error</b>')
        mensaje_informacion.setInformativeText(f"<p style=\"margin-right:25px\">Failed to uninstall {nombre_app} app. Try again, please.")
        layout.addWidget(status_bar, 1, 0, 0, -1)
        mensaje_informacion.exec()


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


class CambiarTema(QObject):
    @pyqtSlot()
    def cambiar_tema(self):
        global tema
        if not os.path.exists(conf):
            if not os.path.exists(conf_dir):
                os.system("mkdir " + conf_dir)
            os.system("touch " + conf)
        else:
            os.system("rm -rf " + conf_dir)
            

visor = QWidget()

layout = QGridLayout()
layout.setContentsMargins(0, 0, 0, 0)
visor.setLayout(layout)


status_bar = QStatusBar()
status_bar.setFixedHeight(20)
layout.addWidget(status_bar, 1, 0, 0, -1) #Que caiga fuera para facilitar las cosas

view = QWebEngineView()
channel = QWebChannel()
view.page().setWebChannel(channel)
botonActivarSoporte = ActivarSoporte()
channel.registerObject("botonInstalarFlatpak", botonActivarSoporte)
botonBuscarApp = BuscarApp()
channel.registerObject("botonBuscar", botonBuscarApp)
botonInstalarApp = InstalarApp()
channel.registerObject("botonInstalarPaquete", botonInstalarApp)
botonDesinstalarApp = DesinstalarApp()
channel.registerObject("botonDesinstalarPaquete", botonDesinstalarApp)
botonAbrirWeb = PaginaWeb()
channel.registerObject("botonAbrirWeb", botonAbrirWeb)
botonActualizarTodo = ActualizarTodo()
channel.registerObject("botonActualizarTodo", botonActualizarTodo)
botonCambiarTema = CambiarTema()
channel.registerObject("botonCambiarTema", botonCambiarTema)
view.page().setHtml(html)                    

layout.addWidget(view, 0, 0, 1, 1)
visor.setMinimumSize(400, 500)
visor.setGeometry(0, 0, 1256, 720)

visor.show()
app.exec()
