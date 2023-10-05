import os
import pickle
from rembg import remove
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog

class BackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Background Remover App")

        self.load_config()
        self.input_folder = tk.StringVar(value=self.config.get('input_folder', ''))
        self.output_folder = tk.StringVar(value=self.config.get('output_folder', ''))

        # Configuración de la interfaz
        self.create_widgets()
        
    def create_widgets(self):
        # Etiquetas
        tk.Label(self.root, text="Carpeta de entrada:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Label(self.root, text="Carpeta de salida:").grid(row=1, column=0, sticky="w", padx=5, pady=5)

        # Campos de entrada
        entry_input = tk.Entry(self.root, textvariable=self.input_folder, width=40, state="readonly")
        entry_input.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Seleccionar Carpeta", command=self.select_input_folder).grid(row=0, column=2, padx=5, pady=5)

        entry_output = tk.Entry(self.root, textvariable=self.output_folder, width=40, state="readonly")
        entry_output.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Seleccionar Carpeta", command=self.select_output_folder).grid(row=1, column=2, padx=5, pady=5)

        # Botones
        tk.Button(self.root, text="Guardar Configuración", command=self.save_config).grid(row=2, column=0, columnspan=3, pady=10)
        tk.Button(self.root, text="Procesar imágenes", command=self.process_images).grid(row=3, column=0, columnspan=3, pady=10)
    
    def select_input_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta de entrada")
        if folder:
            self.input_folder.set(folder)
            self.save_config()

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if folder:
            self.output_folder.set(folder)
            self.save_config()

    def load_config(self):
        try:
            with open('config.pkl', 'rb') as f:
                self.config = pickle.load(f)
        except (FileNotFoundError, pickle.UnpicklingError):
            self.config = {}

    def save_config(self):
        self.config['input_folder'] = self.input_folder.get()
        self.config['output_folder'] = self.output_folder.get()
        with open('config.pkl', 'wb') as f:
            pickle.dump(self.config, f)

    def process_images(self):
        # Obtener la lista de archivos en la carpeta de entrada
        input_folder = self.input_folder.get()
        if not input_folder or not os.path.exists(input_folder):
            tk.messagebox.showerror("Error", "Carpeta de entrada no válida.")
            return

        # Crear la carpeta de salida si no existe
        output_folder = self.output_folder.get()
        if not output_folder:
            tk.messagebox.showerror("Error", "Carpeta de salida no válida.")
            return
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Iterar sobre cada archivo en la carpeta de entrada
        input_files = os.listdir(input_folder)
        for input_file in input_files:
            # Construir la ruta completa de entrada
            input_path = os.path.join(input_folder, input_file)

            # Construir la ruta completa de salida
            output_file = os.path.splitext(input_file)[0] + '_output.png'
            output_path = os.path.join(output_folder, output_file)

            # Abrir la imagen de entrada
            input_image = Image.open(input_path)

            # Eliminar el fondo y redimensionar la imagen
            output_image = remove(input_image)
            width, height = output_image.size
            aspect_ratio = width / height

            max_size = 1000
            if width > height:
                new_width = max_size
                new_height = int(max_size / aspect_ratio)
            else:
                new_height = max_size
                new_width = int(max_size * aspect_ratio)

            output_image_resized = output_image.resize((new_width, new_height), Image.ANTIALIAS)

            # Mostrar la imagen resultante en una ventana de vista previa
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Vista previa")
            photo = ImageTk.PhotoImage(output_image_resized)
            label = tk.Label(preview_window, image=photo)
            label.image = photo
            label.pack()

            # Pedir al usuario que ingrese un nuevo nombre para la imagen
            new_name = tk.simpledialog.askstring("Cambiar nombre", f"Ingrese un nuevo nombre para {input_file} (sin extensión):")
            
            if new_name:
                # Guardar la imagen resultante con el nuevo nombre y extensión .png
                new_name_with_extension = new_name + ".png"
                new_output_path = os.path.join(output_folder, new_name_with_extension)
                output_image_resized.save(new_output_path)

                # Cerrar la ventana de vista previa después de guardar la imagen con el nuevo nombre
                preview_window.destroy()

        # Limpiar la lista de imágenes procesadas después de procesar todas las imágenes
        self.processed_images = []

if __name__ == "__main__":
    root = tk.Tk()
    app = BackgroundRemoverApp(root)
    root.mainloop()
