# gui.py — Interfaz gráfica para el conversor CFE → TXT Memory

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import logging
import ctypes

# Hacer que Windows use el ícono de la app en la barra de tareas, no el de Python
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("cfe_converter")


def resource_path(relative_path):
    """Obtiene la ruta correcta tanto en desarrollo como empaquetado con PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

from reader import leer_excel
from rules import generar_asientos
from writer import escribir_txt


class TextHandler(logging.Handler):
    """Handler de logging que escribe en un widget ScrolledText de tkinter."""

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record) + "\n"
        self.text_widget.after(0, self._append, msg, record.levelno)

    def _append(self, msg, levelno):
        self.text_widget.configure(state="normal")
        if levelno >= logging.ERROR:
            tag = "error"
        elif levelno >= logging.WARNING:
            tag = "warning"
        else:
            tag = "info"
        self.text_widget.insert(tk.END, msg, tag)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state="disabled")


class CFEConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CFE Converter - Conversor CFE a Memory")
        self.root.geometry("780x680")
        self.root.minsize(650, 550)
        self.root.configure(bg="#f0f0f0")

        self._load_logo()
        self._processing = False
        self._build_ui()
        self._setup_logging()

    def _load_logo(self):
        """Carga el logo .ico para la barra de título y barra de tareas de Windows."""
        try:
            ico_path = resource_path("logo.ico")
            if os.path.isfile(ico_path):
                self.root.iconbitmap(ico_path)
        except Exception:
            pass

    def _build_ui(self):
        # --- Estilo ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"), background="#f0f0f0")
        style.configure("TLabel", font=("Segoe UI", 10), background="#f0f0f0")
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"), padding=10)
        style.configure("TEntry", font=("Segoe UI", 10))
        style.configure("Status.TLabel", font=("Segoe UI", 9), background="#e0e0e0")

        main = ttk.Frame(self.root, padding=15)
        main.pack(fill=tk.BOTH, expand=True)

        # --- Título ---
        ttk.Label(main, text="Conversor CFE a formato Memory", style="Title.TLabel").pack(anchor="w")
        ttk.Separator(main, orient="horizontal").pack(fill=tk.X, pady=(5, 12))

        # --- Archivo de entrada ---
        frame_input = ttk.LabelFrame(main, text="Archivo CFE de entrada (.xls / .xlsx)", padding=8)
        frame_input.pack(fill=tk.X, pady=(0, 8))

        row_input = ttk.Frame(frame_input)
        row_input.pack(fill=tk.X)

        self.var_input = tk.StringVar()
        entry_input = ttk.Entry(row_input, textvariable=self.var_input, font=("Segoe UI", 10))
        entry_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        btn_input = ttk.Button(row_input, text="Examinar...", command=self._browse_input)
        btn_input.pack(side=tk.RIGHT)

        # --- Carpeta de salida ---
        frame_output = ttk.LabelFrame(main, text="Carpeta de salida", padding=8)
        frame_output.pack(fill=tk.X, pady=(0, 8))

        row_output = ttk.Frame(frame_output)
        row_output.pack(fill=tk.X)

        self.var_output = tk.StringVar()
        entry_output = ttk.Entry(row_output, textvariable=self.var_output, font=("Segoe UI", 10))
        entry_output.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        btn_output = ttk.Button(row_output, text="Examinar...", command=self._browse_output)
        btn_output.pack(side=tk.RIGHT)

        # --- Nombre archivo salida ---
        frame_name = ttk.Frame(main)
        frame_name.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_name, text="Nombre del archivo de salida (sin .txt):").pack(side=tk.LEFT)
        self.var_nombre = tk.StringVar()
        entry_name = ttk.Entry(frame_name, textvariable=self.var_nombre, width=30, font=("Segoe UI", 10))
        entry_name.pack(side=tk.LEFT, padx=(6, 0))

        # --- Botón convertir ---
        self.btn_convert = ttk.Button(
            main, text="Convertir", style="Accent.TButton", command=self._start_conversion
        )
        self.btn_convert.pack(pady=(0, 10))

        # --- Barra de progreso ---
        self.progress = ttk.Progressbar(main, mode="indeterminate", length=300)
        self.progress.pack(fill=tk.X, pady=(0, 8))

        # --- Log de salida ---
        frame_log = ttk.LabelFrame(main, text="Registro de actividad", padding=5)
        frame_log.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            frame_log, height=12, state="disabled",
            font=("Consolas", 9), wrap=tk.WORD, bg="#1e1e1e", fg="#d4d4d4",
            insertbackground="white",
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.tag_config("error", foreground="#f44747")
        self.log_text.tag_config("warning", foreground="#cca700")
        self.log_text.tag_config("info", foreground="#d4d4d4")

        # --- Barra de estado ---
        self.var_status = tk.StringVar(value="Listo")
        status_bar = ttk.Label(
            self.root, textvariable=self.var_status, style="Status.TLabel",
            relief=tk.SUNKEN, anchor=tk.W, padding=(6, 3),
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _setup_logging(self):
        handler = TextHandler(self.log_text)
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        # Remove existing handlers to avoid duplicate console output
        root_logger.handlers.clear()
        root_logger.addHandler(handler)

    def _browse_input(self):
        path = filedialog.askopenfilename(
            title="Seleccionar archivo CFE",
            filetypes=[
                ("Archivos Excel", "*.xls *.xlsx"),
                ("Todos los archivos", "*.*"),
            ],
        )
        if path:
            self.var_input.set(path)
            # Auto-fill nombre from input filename
            if not self.var_nombre.get():
                base = os.path.splitext(os.path.basename(path))[0]
                self.var_nombre.set(base)
            # Auto-fill output dir
            if not self.var_output.get():
                self.var_output.set(os.path.dirname(path))

    def _browse_output(self):
        path = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if path:
            self.var_output.set(path)

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")

    def _start_conversion(self):
        if self._processing:
            return

        ruta_input = self.var_input.get().strip()
        carpeta_output = self.var_output.get().strip()
        nombre = self.var_nombre.get().strip()

        if not ruta_input:
            messagebox.showwarning("Falta dato", "Seleccione un archivo CFE de entrada.")
            return
        if not os.path.isfile(ruta_input):
            messagebox.showerror("Error", f"El archivo no existe:\n{ruta_input}")
            return
        if not carpeta_output:
            messagebox.showwarning("Falta dato", "Seleccione una carpeta de salida.")
            return
        if not nombre:
            nombre = os.path.splitext(os.path.basename(ruta_input))[0]
            self.var_nombre.set(nombre)

        self._processing = True
        self.btn_convert.configure(state="disabled")
        self.progress.start(15)
        self.var_status.set("Procesando...")
        self._clear_log()

        thread = threading.Thread(
            target=self._run_conversion,
            args=(ruta_input, carpeta_output, nombre),
            daemon=True,
        )
        thread.start()

    def _run_conversion(self, ruta_input, carpeta_output, nombre):
        logger = logging.getLogger(__name__)
        try:
            ruta_txt = os.path.join(carpeta_output, f"{nombre}.txt")

            logger.info(f"Leyendo archivo CFE: {ruta_input}")
            registros = leer_excel(ruta_input)

            if not registros:
                logger.error("No se encontraron registros CFE en el archivo.")
                self.root.after(0, self._conversion_done, False, "")
                return

            logger.info(f"Se encontraron {len(registros)} comprobantes.")

            todos_asientos = []
            errores = 0
            ruts_desconocidos = set()

            for idx, reg in enumerate(registros, start=1):
                asientos = generar_asientos(reg, fila_num=idx)
                if asientos:
                    todos_asientos.extend(asientos)
                else:
                    errores += 1

            if not todos_asientos:
                logger.error("No se generaron asientos. Revise los datos de entrada.")
                self.root.after(0, self._conversion_done, False, "")
                return

            escribir_txt(todos_asientos, ruta_txt)

            logger.info("=" * 50)
            logger.info("RESUMEN")
            logger.info(f"  CFEs leidos:        {len(registros)}")
            logger.info(f"  Asientos generados: {len(todos_asientos)}")
            if errores:
                logger.info(f"  CFEs con error:     {errores}")
            logger.info(f"  Archivo de salida:  {ruta_txt}")
            logger.info("=" * 50)

            self.root.after(0, self._conversion_done, True, ruta_txt)

        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            self.root.after(0, self._conversion_done, False, "")

    def _conversion_done(self, success, ruta_txt):
        self.progress.stop()
        self._processing = False
        self.btn_convert.configure(state="normal")

        if success:
            self.var_status.set(f"Completado: {ruta_txt}")
            messagebox.showinfo(
                "Conversion exitosa",
                f"Archivo generado correctamente:\n{ruta_txt}",
            )
        else:
            self.var_status.set("Error en la conversion")


def main():
    root = tk.Tk()
    app = CFEConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
