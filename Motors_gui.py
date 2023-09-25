import serial
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import time

# Crear la imagen en blanco
width, height = 640, 480
blank_image = Image.new('RGB', (width, height), color='white')

# Guardar la imagen en blanco como un archivo PNG
blank_image.save('blank_image.png')



Desire_angles = [
    [0, 0, 0, 0], [0, 0, 0, 90], [0, 0, -45, 45], [0, 0, 0, 45],
    [90, 90, 0, 0], [90, 90, 0, 90], [90, 90, -45, 45], [90, 90, 0, 45],
    [45, 45, 0, 0], [45, 45, 0, 90], [45, 45, -45, 45], [45, 45, 0, 45],
    [45, 90, 0, 0], [45, 90, 0, 90], [45, 90, 45, 45], [45, 90, 0, 45],
    [0, 0, 0, 0]
]

# Define los pines y configuraciones para los motores
Motors = [
    {'pin': 1, 'speed': 50, 'acceleration': 751},
    {'pin': 2, 'speed': 50, 'acceleration': 720},
    {'pin': 3, 'speed': 50, 'acceleration': 636},
    {'pin': 4, 'speed': 50, 'acceleration': 743}
]   

class MotorControlApp:
    def __init__(self, root):

        self.root = root
        self.root.title('Control de Motores')

        self.serial_obj = None
        self.com_var = tk.StringVar()

        # Cargar la imagen en blanco desde el archivo PNG
        self.blank_image_tk = ImageTk.PhotoImage(file='blank_image.png')

        self.create_ui()

        
    def create_ui(self):
        self.create_com_frame()
        self.create_motor_frame()
        self.create_image_frame()

    def create_com_frame(self):
        com_frame = tk.Frame(self.root)
        com_frame.pack(pady=10)

        com_label = tk.Label(com_frame, text='Seleccionar Puerto:')
        com_label.pack(side=tk.LEFT, padx=5)

        com_combobox = ttk.Combobox(com_frame, textvariable=self.com_var, values=self.get_available_ports())
        com_combobox.pack(side=tk.LEFT, padx=5)

        conectar_button = tk.Button(com_frame, text='Conectar', command=self.conectar_puerto)
        conectar_button.pack(side=tk.LEFT, padx=5)

        desconectar_button = tk.Button(com_frame, text='Desconectar', command=self.desconectar_puerto)
        desconectar_button.pack(side=tk.LEFT, padx=5)

    def create_motor_frame(self):
        motor_frame = tk.Frame(self.root)
        motor_frame.pack(pady=10)

        motor_label = tk.Label(motor_frame, text='Control de Motores:')
        motor_label.pack()

        open_button = tk.Button(motor_frame, text='Abrir Shutter', command=self.abrir_shutter)
        open_button.pack(pady=5)

        close_button = tk.Button(motor_frame, text='Cerrar Shutter', command=self.cerrar_shutter)
        close_button.pack(pady=5)

        velocidad_label = tk.Label(motor_frame, text='Velocidad:')
        velocidad_label.pack()

        self.velocidad_entry = tk.Entry(motor_frame)
        self.velocidad_entry.pack()

        cambiar_velocidad_button = tk.Button(motor_frame, text='Cambiar Velocidad', command=self.cambiar_velocidad)
        cambiar_velocidad_button.pack(pady=5)

        pasos_label = tk.Label(motor_frame, text='Pasos:')
        pasos_label.pack()

        self.pasos_entry = tk.Entry(motor_frame)
        self.pasos_entry.pack()

        mover_motor_button = tk.Button(motor_frame, text='Mover Motor', command=self.mover_motor)
        mover_motor_button.pack(pady=5)

        iniciar_motor_button = tk.Button(motor_frame, text='Iniciar Motor', command=self.iniciar_motor)
        iniciar_motor_button.pack(pady=5)

        detener_motor_button = tk.Button(motor_frame, text='Detener Motor', command=self.detener_motor)
        detener_motor_button.pack(pady=5)

        obtener_velocidad_button = tk.Button(motor_frame, text='Obtener Velocidad', command=self.obtener_velocidad)
        obtener_velocidad_button.pack(pady=5)

        # Nuevo botón para iniciar análisis completo
        iniciar_analisis_button = tk.Button(motor_frame, text='Iniciar Análisis', command=self.rotate_and_acquire_images)
        iniciar_analisis_button.pack(pady=20)

    def create_image_frame(self):
        image_frame = tk.Frame(self.root)
        image_frame.pack(pady=10)

        self.image_label = tk.Label(image_frame)
        self.image_label.pack()
    def clean_up_images(self):
        # Eliminar todas las imágenes creadas por Tkinter
        for img in self.root.winfo_toplevel().tk.call('image', 'names'):
            self.root.winfo_toplevel().tk.call('image', 'delete', img)
    def get_available_ports(self):
        return [f'COM{i+1}' for i in range(256)]

    def conectar_puerto(self):
        com_port = self.com_var.get()
        try:
            self.serial_obj = serial.Serial(com_port, 9600, timeout=1)
            messagebox.showinfo('Conexión Exitosa', f'Puerto {com_port} conectado.')
        except serial.SerialException:
            messagebox.showerror('Error de Conexión', f'No se pudo conectar al puerto {com_port}.')

    def desconectar_puerto(self):
        if self.serial_obj is not None:
            self.serial_obj.close()
            self.serial_obj = None
            messagebox.showinfo('Desconexión', 'Puerto desconectado correctamente.')

    def enviar_comando(self, comando):
        if self.serial_obj is not None and self.serial_obj.is_open:
            self.serial_obj.write(comando.encode('utf-8'))
            respuesta = self.serial_obj.read().decode('utf-8')
            return respuesta
        else:
            messagebox.showerror('Error', 'No se ha establecido la conexión al puerto.')

    def abrir_shutter(self):
        respuesta = self.enviar_comando('O')
        if respuesta == 'F':
            messagebox.showinfo('Éxito', 'Shutter abierto con éxito.')
        else:
            messagebox.showerror('Error', 'Error al abrir el shutter.')

    def cerrar_shutter(self):
        respuesta = self.enviar_comando('N')
        if respuesta == 'F':
            messagebox.showinfo('Éxito', 'Shutter cerrado con éxito.')
        else:
            messagebox.showerror('Error', 'Error al cerrar el shutter.')

    def cambiar_velocidad(self):
        velocidad = self.velocidad_entry.get()
        if velocidad.isdigit():
            self.enviar_comando('C' + velocidad)
            messagebox.showinfo('Éxito', 'Velocidad cambiada con éxito.')
        else:
            messagebox.showerror('Error', 'Ingresa un valor numérico válido.')

    def mover_motor(self):
        pasos = self.pasos_entry.get()
        if pasos.isdigit():
            self.enviar_comando('P' + pasos)
            messagebox.showinfo('Éxito', 'Motor movido con éxito.')
        else:
            messagebox.showerror('Error', 'Ingresa un valor numérico válido.')

    def iniciar_motor(self):
        velocidad = self.velocidad_entry.get()
        if velocidad.isdigit():
            self.enviar_comando('R')
        else:
            messagebox.showerror('Error', 'Ingresa un valor numérico válido.')

    def detener_motor(self):
        self.enviar_comando('S')
        messagebox.showinfo('Éxito', 'Motor detenido con éxito.')

    def obtener_velocidad(self):
        velocidad = self.enviar_comando('V')
        messagebox.showinfo('Velocidad actual', f'La velocidad actual es: {velocidad}')
        

   
    def rotate_and_acquire_images(self):
        if self.serial_obj is not None and self.serial_obj.is_open:
            # Verifica la comunicación con Arduino
            if self.send_command('H') == b'Y':
                print('Comunicación serial con Arduino establecida.')

                # Realiza la rutina de ángulos
                for k in range(len(Desire_angles)):
                    for m in range(4):
                        # Ignora posiciones angulares repetidas
                        if k > 0 and Desire_angles[k - 1][m] == Desire_angles[k][m]:
                            continue

                        # Define el ángulo deseado actual para el motor m
                        motor = Motors[m]
                        motor['desire_angle'] = Desire_angles[k][m]

                        # Envía el comando para mover el motor al ángulo deseado actual
                        self.send_command('P', motor['pin'], motor['desire_angle'])

                        # Espera un tiempo antes de tomar la siguiente medida
                        time.sleep(0.05)

                        # Toma una imagen si no es la última medida
                        if k < len(Desire_angles) - 1:
                            print(f'Medición {k}')
                            image = self.acquire_image()

                            # Procesa y muestra la imagen o la imagen en blanco si no hay imagen
                            if image is not None:
                                self.show_image(image)
                            else:
                                self.show_blank_image()

    def show_image(self, image):
        # Convertir la imagen de OpenCV a una imagen de Tkinter
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image_tk = ImageTk.PhotoImage(image)

        # Mostrar la imagen en el cuadro de imagen
        self.image_label.configure(image=image_tk)
        self.image_label.image = image_tk


    def show_blank_image(self):
         # Mostrar la imagen en blanco en el cuadro de imagen
         self.image_label.configure(image=self.blank_image_tk)
         self.image_label.image = self.blank_image_tk
        
if __name__ == '__main__':
    root = tk.Tk()
    app = MotorControlApp(root)

    # Agregar lista desplegable para seleccionar la cámara
    camera_frame = tk.Frame(root)
    camera_frame.pack(pady=10)

    camera_label = tk.Label(camera_frame, text='Seleccionar Cámara:')
    camera_label.pack(side=tk.LEFT, padx=5)

    app.camera_var = tk.StringVar()
    app.camera_combobox = ttk.Combobox(camera_frame, textvariable=app.camera_var)
    app.camera_combobox.pack(side=tk.LEFT, padx=5)

    # Obtener las cámaras disponibles y establecer la primera como seleccionada por defecto
    available_cameras = [str(i) for i in range(10)]
    app.camera_combobox['values'] = available_cameras
    app.camera_var.set(available_cameras[0])

    root.protocol("WM_DELETE_WINDOW", app.clean_up_images)
    root.mainloop()
