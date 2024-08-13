import cv2  # Importa la biblioteca OpenCV para el procesamiento de imágenes
from kivy.app import App  # Importa la clase base para todas las aplicaciones de Kivy
from kivy.uix.boxlayout import BoxLayout  # Importa el diseño de caja para organizar widgets
from kivy.uix.image import Image  # Importa el widget de imagen para mostrar la cámara
from kivy.clock import Clock  # Importa el reloj para programar funciones
from kivy.graphics.texture import Texture  # Importa las texturas para manipular imágenes


class FaceDetectionApp(App):
    def build(self):
        # Crea un layout vertical para organizar widgets
        layout = BoxLayout(orientation='vertical')

        # Crea un widget de imagen que mostrará la cámara
        self.img = Image(size_hint=(1, 1), allow_stretch=True, keep_ratio=False)
        layout.add_widget(self.img)

        # Inicia la captura de video con OpenCV
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Carga el modelo preentrenado de detección facial de OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Programa la función que actualizará la imagen de la cámara
        Clock.schedule_interval(self.update, 1.0 / 30.0)  # 30 FPS

        return layout

    def update(self, dt):
        # Lee un frame de la cámara
        ret, frame = self.capture.read()

        if ret:
            # Convierte el frame a escala de grises
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detecta caras en el frame
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

            # Dibuja rectángulos alrededor de las caras detectadas
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Convierte el frame de BGR (formato de OpenCV) a RGB (formato de Kivy)
            buf = cv2.flip(frame, 0).tostring()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img.texture = image_texture

    def on_stop(self):
        # Libera la cámara al cerrar la aplicación
        self.capture.release()


if __name__ == '__main__':
    FaceDetectionApp().run()
