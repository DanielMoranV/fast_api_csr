import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from dotenv import load_dotenv, set_key
import os

# Cargar variables de entorno
dotenv_path = ".env"
load_dotenv(dotenv_path)

process = None  # Variable global para manejar el proceso del servidor


def start_server(output_widget):
    global process
    try:
        # Configuración para evitar abrir una consola adicional
        process = subprocess.Popen(
            [r"venv\Scripts\uvicorn.exe", "api:app", "--host",
                "0.0.0.0", "--port", "8000", "--reload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW  # Evita abrir una consola
        )

        # Leer la salida del servidor y mostrarla en la interfaz gráfica
        def read_output():
            for line in process.stdout:
                # Agrega la línea al widget de salida
                output_widget.insert(tk.END, line)
                # Desplaza hacia abajo automáticamente
                output_widget.see(tk.END)

        threading.Thread(target=read_output, daemon=True).start()
    except FileNotFoundError as e:
        messagebox.showerror("Error", f"Uvicorn no encontrado: {str(e)}")
    except Exception as e:
        messagebox.showerror(
            "Error", f"Error al iniciar el servidor: {str(e)}")


def stop_server():
    global process
    if process and process.poll() is None:  # Verifica si el proceso está activo
        process.terminate()
        process = None
        messagebox.showinfo("Servidor", "Servidor detenido correctamente.")


def save_data_source(new_data_source):
    """Guarda el nuevo valor de DATA_SOURCE en el archivo .env."""
    try:
        set_key(dotenv_path, "DATA_SOURCE", new_data_source)
        messagebox.showinfo(
            "Guardado", "DATA_SOURCE actualizado correctamente.")
    except Exception as e:
        messagebox.showerror(
            "Error", f"No se pudo guardar DATA_SOURCE: {str(e)}")


def browse_data_source(entry):
    """Abre un diálogo para seleccionar una carpeta y actualiza el campo de texto."""
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry.delete(0, tk.END)
        entry.insert(0, folder_selected)


# Interfaz gráfica
def create_gui():
    root = tk.Tk()
    root.title("Gestión de Servidor API")

    # Campo de texto para la salida del servidor
    output_widget = tk.Text(root, height=20, width=80)
    output_widget.pack(padx=10, pady=10)

    # Botón para iniciar el servidor
    start_button = tk.Button(
        root, text="Iniciar Servidor", command=lambda: start_server(output_widget)
    )
    start_button.pack(side=tk.LEFT, padx=10, pady=10)

    # Botón para detener el servidor
    stop_button = tk.Button(root, text="Detener Servidor", command=stop_server)
    stop_button.pack(side=tk.RIGHT, padx=10, pady=10)

    # Campo para editar DATA_SOURCE
    data_source_frame = tk.Frame(root)
    data_source_frame.pack(padx=10, pady=10)

    tk.Label(data_source_frame, text="DATA_SOURCE:").pack(side=tk.LEFT, padx=5)
    data_source_entry = tk.Entry(data_source_frame, width=50)
    data_source_entry.pack(side=tk.LEFT, padx=5)

    # Cargar valor actual de DATA_SOURCE
    current_data_source = os.getenv("DATA_SOURCE", "")
    data_source_entry.insert(0, current_data_source)

    browse_button = tk.Button(
        data_source_frame, text="Seleccionar Carpeta", command=lambda: browse_data_source(data_source_entry)
    )
    browse_button.pack(side=tk.LEFT, padx=5)

    save_button = tk.Button(
        root, text="Guardar DATA_SOURCE", command=lambda: save_data_source(data_source_entry.get())
    )
    save_button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
