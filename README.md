<h3 align="center">GymGPT API</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---


## 📝 Table of Contents

- [Acerca del Proyecto](#about)
- [Iniciando](#getting_started)
- [Deployment](#deployment)
- [Uso](#usage)
- [Construcción del proyecto](#built_using)
- [Autores](#authors)
- [Agradecimientos](#acknowledgement)

## 🧐 Acerca del Proyecto <a name = "about"></a>

Este proyecto, GymGPT API, tiene como objetivo proporcionar un Backend de la aplicación GymGPT la cual, permitira a los usuarios gestionar sus actividades en el gimnasio estando informados sobre las maquinas. Desarrollado con un enfoque en la simplicidad y la funcionalidad, esta aplicación utiliza REACT CLI para el frontend, ofreciendo una interfaz de usuario interactiva y fácil de usar, y Python Django para el backend, asegurando un manejo robusto y eficiente de los datos.

La aplicación permite a los usuarios escanear las maquinas y comprender el uso, además de marcar y llevar un seguimiento sobre ellas. Con un diseño responsivo y una arquitectura de API RESTful, GymGPT está construido para adaptarse a diversas necesidades, desde el uso personal hasta la integración en entornos de Gimnasio. Esta combinación de tecnologías modernas y buenas prácticas de desarrollo garantiza una experiencia fluida y confiable para el usuario final.

## 🏁 Primeros Pasos <a name = "getting_started"></a>

Estas instrucciones te permitirán obtener una copia del proyecto y ejecutarlo en tu máquina local para propósitos de desarrollo y pruebas. Consulta la sección de [despliegue](#deployment) para obtener notas sobre cómo desplegar el proyecto en un sistema en vivo.

### Prerrequisitos

Asegúrate de tener instaladas las siguientes herramientas:

- [Python Django](https://www.djangoproject.com/) (versión 5.1 o superior)
- [MySQL](https://www.mysql.com/products/workbench/) para la base de datos

### Instalación

Sigue estos pasos para configurar el proyecto en tu entorno local:

1. Clona el repositorio:

    ```bash
    git clone https://github.com/Blap00/GymGPT-API.git
    cd GymGPT
    ```

2. Configura el Ambiente virtual:

    1. ejecuta el correspondiente VENV:

        ```bash
        python -m venv venv
        ```
        ```bash
        /venv/Scripts/activate
        ```
        

    2. Instala las dependencias necesarias:

        ```bash
        pip install -r requirements.txt
        ```

    3. Configura la base de datos SQLITE:

        - Configura la base de datos SQLITE segun el requerimiento.

    4. Ejecuta las migraciones para crear las tablas necesarias:

        ```bash
        python manage.py makemigrations
        python manage.py migrate
        ```

    5. Inicia el servidor:

        ```bash
        python manage.py runserver
        ```

### Estructura del Proyecto

El proyecto está dividido en dos partes principales:

- **Backend**: Ubicado en el repositorio `GymGPT-API`, manejado por Python Django.
- **Frontend**: Ubicado en el repositorio `GymGPT-FRONT`, construido con React para manejar las solicitudes HTTP.

### Ejecución

Una vez completados los pasos anteriores, deberías poder acceder a la aplicación en tu navegador en la dirección `http://localhost:8000` para el frontend y `http://localhost:3000` para la API del backend.

¡Ya estás listo para comenzar a desarrollar y probar el proyecto!


## ⛏️ Build fue realizada gracias a <a name = "built_using"></a>


- [Python Django](https://www.djangoproject.com/)

## ✍️ Autores <a name = "authors"></a>

- [@Blap00](https://github.com/Blap00) - Desarrollador del sistema
- [@MoonLight-coder](https://github.com/MoonLight-coder) - Colaborador del Sistema
- [@AstrovC](https://github.com/AstrovC) - Colaborador del Sistema
