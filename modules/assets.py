css = """
    body {
        background-color: var(--fondo);
        color: var(--texto);
    }

    #h1_flatpik {
        color: var(--texto);
        text-align: center;
        font-size: 1.6rem;
        transition: 1s;
        position: fixed;
        top: 0;
        left:0;
        z-index: 112;
        background-color: var(--fondo2);
        margin: 0;
        width: 100vw;
    }

    #h1_flatpik + * {
        margin-top:180px;
    }

    @keyframes fundido_entrada {
        from {
            opacity: 0;
        }

        to {
            opacity: 1;
        }
    }

     @keyframes desplazamiento_arriba {
        0% {
            top: 100px;
        }

        50% {
            top: -15px;
        }

        100% {
            top: 0;
        }
    }

    #h2_busqueda {
        text-align: center;
        margin-bottom: -20px;
        animation: fundido_entrada 1s
    }

    ::-webkit-scrollbar {
        width: 0px;
    }

    #soporte:focus, #buscar input:focus, #actualizar:focus {
        outline: none;
    }

    #buscar button:focus, .instalar:focus, .desinstalar:focus {
        outline: none;
        box-shadow: 1px 1px 3px grey
    }


    #soporte, #botonArriba, #actualizar {
        background-color: var(--fondo3);
        border: 2px solid var(--texto);
        color: var(--texto);
        font-size: 1.7rem;
        transition: .2s;
        border-radius: 5px;
        position: fixed;
        z-index:111;
    }

    #soporte, #actualizar {
        left: 10px;
        bottom: 10px;
        padding: 3px 7px;
    }

    #botonArriba {
        bottom: 10px;
        right: -135px;
        font-size: 30px;
        font-weight: bolder;
        padding: 3px 12px;
        outline: none
    }

    #soporte:hover, #actualizar:hover, #buscar button:hover, .instalar:hover, .desinstalar:hover, #botonArriba:hover {
        background-color: var(--texto);
        border: 2px solid var(--texto);
        color: var(--fondo3);
        cursor: pointer
    }

    #soporte:hover + #tipsoporte, #actualizar:hover + #tipactualizartodo {
        opacity:1;
    }

    #tipsoporte, #tipactualizartodo {
        color: var(--texto);
        font-size: 1.2rem;
        position: fixed;
        opacity: 0;
        transition: .3s;
        text-shadow: 2px 2px 2px black, 1px 1px 1px black, 3px 3px 3px black;
        z-index:111;
    }

    #tipsoporte, #tipactualizartodo {
        left: 60px;
        bottom: 18px;        
    }

    #actualizar {
        padding-left: 12px
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
        background-color: var(--fondo4);
        border: 2px solid var(--fondo2);
        border-radius: 5px
    }

    #buscar button {
        background-color: var(--fondo3);
        border: 2px solid var(--texto);
        color: var(--texto);
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
        justify-content: center;
        animation: fundido_entrada 1s
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
        background-color: var(--fondoArticle);
        animation: desplazamiento_arriba 1s
    }

    #resultados h2 {
        font-size: 1.2rem;
        padding: 0;
        cursor: pointer
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

    .instalar, .desinstalar{
        background-color: var(--fondo3);
        border: 2px solid var(--texto);
        color: var(--texto);
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

    #interruptor {
        color: var(--texto);
        position: fixed;
        top: 2px;
        right: 5px;
        z-index:1111;
        cursor: pointer;
        font-size: 1.5rem;
    }


</style>"""

javascript= """<script>
     setTimeout(function() {
        document.getElementById("busqueda").select();
    }, 100); 

    let objetoInstalarFlatpak = null;
    let objetoBuscar = null;
    let objetoInstalarPaquete = null;
    let objetoDesinstalarPaquete = null;
    let objetoAbrirWeb = null;
    let objetoActualizarTodo = null;
    let objetoCambiarTema = null;
    new QWebChannel(qt.webChannelTransport, function (channel) {
        objetoInstalarFlatpak = channel.objects.botonInstalarFlatpak;
        objetoBuscar = channel.objects.botonBuscar;
        objetoInstalarPaquete = channel.objects.botonInstalarPaquete;
        objetoDesinstalarPaquete = channel.objects.botonDesinstalarPaquete;
        objetoAbrirWeb = channel.objects.botonAbrirWeb;
        objetoActualizarTodo = channel.objects.botonActualizarTodo;
        objetoCambiarTema = channel.objects.botonCambiarTema;
    });

    function activar_soporte() {
        objetoInstalarFlatpak.activar_soporte();
    }

    function actualizar_todo() {
        objetoActualizarTodo.actualizar_todo();
        document.getElementById('actualizar').style.display= "none"
    }

    function enviar_busqueda() {
        let busqueda = document.getElementById('busqueda').value;
        objetoBuscar.buscarApp(busqueda)
    }


    function instalar_paquete(id_app, nombre_app) {
        objetoInstalarPaquete.instalar_paquete(id_app, nombre_app);
    }

    function desinstalar_paquete(id_app, nombre_app) {
        objetoDesinstalarPaquete.desinstalar_paquete(id_app, nombre_app);
    }

    function abrir_web(url) {
        objetoAbrirWeb.abrir_pagina_web(url);
    }

    document.getElementById("busqueda").addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            document.getElementById("enviar_busqueda").click();
        }
    });

    document.body.addEventListener("keydown", function(event) {
        if (event.ctrlKey && event.key === "f") {
            funcionArriba()
        }
    });



    window.onscroll = function() {
        scrollFunction();
        volverArriba()
    };

    function scrollFunction() {
        if (document.body.scrollTop > 120) {
            document.getElementById("h1_flatpik").style.fontSize = "0.45rem";
        } else {
            document.getElementById("h1_flatpik").style.fontSize = "1.6rem";
        }
    }

    let botonArriba = document.getElementById("botonArriba");

    function volverArriba() {
        if (document.body.scrollTop > 400 || document.documentElement.scrollTop > 400) {
            botonArriba.style.right = "10px";
        } else {
            botonArriba.style.right = "-115px";
        }
    }

    function funcionArriba() {
        document.body.scrollTop = 0;
        document.getElementById('busqueda').focus()
    }


    function cambiarTema() {
        objetoCambiarTema.cambiar_tema();
        enviar_busqueda();
    }

</script>"""