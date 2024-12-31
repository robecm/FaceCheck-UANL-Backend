# FaceCheck UANL

Proyecto desarrollado por Alphaware Team, apoyado por Accenture.

## Descripción

FaceCheck UANL está siendo desarrollado por el equipo de desarrollo Alphaware, parte del capítulo estudiantil CEATI, en colaboración con Accenture para capacitaciones. El propósito del proyecto es crear una aplicación móvil que permita registrar estudiantes, administrativos y profesores. Utilizando reconocimiento facial, la aplicación verifica la identidad de los estudiantes al ingresar a un aula para presentar evaluaciones, evitando fraudes de identidad.

## Tecnologías Utilizadas

- **Backend:** Python con la librería [deepface](https://github.com/serengil/deepface) para el reconocimiento facial.
- **Frontend:** Desarrollo de aplicaciones móviles con [Kivy](https://kivy.org/).

## Instalación

Para instalar y configurar el entorno de desarrollo, sigue estos pasos:

1. Clona el repositorio:
   ```bash
   git clone https://github.com/robecm/FaceCheck-UANL.git
   cd FaceCheck-UANL
   ```

2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Contribuir

Si deseas contribuir al proyecto, por favor sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza los cambios necesarios y haz commit (`git commit -am 'Añadir nueva funcionalidad'`).
4. Sube los cambios a tu rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.
