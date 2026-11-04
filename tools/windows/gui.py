"""Experimental Windows front-end for this fork of xenosworks/xsdk (MIT)."""
import json
import os
import queue
import subprocess
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from build_plan import plan
from i18n import LANGUAGES, translate
from options import BUILD_TYPES, MAKE_TARGETS
from manager import inspect

ROOT = Path(__file__).resolve().parents[2]
CREDITS = """xSDK original: Mena / xenosworks — MIT
https://github.com/xenosworks/xsdk
Port experimental para Windows e interfaz: Axel, con asistencia de OpenAI Codex.
Se conservan LICENSE y THIRD_PARTY_NOTICES.md.
Xenia y libxenon: componentes BSD según los avisos originales.
GCC, binutils, newlib, glslang-xenon y MSYS2 conservan sus propias licencias.
No es un producto oficial de Microsoft ni de xenosworks.
No amplía el compilador de VS2010 y no requiere el XDK de Microsoft.
"""


class App:
    def __init__(self, window):
        self.window = window
        self.events = queue.Queue()
        self.process = None
        self.busy = False
        self.cancelled = threading.Event()
        self.folder = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "xsdk-windows"
        self.settings_path = self.folder / "settings.json"
        defaults = {"msys": "C:/msys64", "sdk": str(ROOT),
                    "prefix": "C:/xsdk-tools/compiler", "work": "C:/xsdk-tools/work", "project": "", "jobs": "4",
                    "sdl": "", "build_type": "Release", "cmake_args": "[]", "target": "cmake_check",
                    "auto_update": "0", "glslang": "", "rom": "", "language": "en", "restore_inputs": "0"}
        try:
            saved = json.loads(self.settings_path.read_text(encoding="utf-8"))
            defaults.update({key: str(value) for key, value in saved.items() if key in defaults})
        except (OSError, ValueError, AttributeError):
            pass
        self.fields = {name: tk.StringVar(value=value) for name, value in defaults.items()}
        self.status = tk.StringVar(value="Port experimental — aún requiere validación completa en Windows")
        window.title("xSDK para Windows — experimental")
        window.geometry("1180x920")
        panel = ttk.Frame(window, padding=14)
        panel.pack(fill="both", expand=True)
        ttk.Label(panel, text="xSDK · Windows", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(panel, text="Compilador PowerPC, shaders y ejemplos · sin Debian ni WSL").pack(
            anchor="w", pady=(0, 12))
        language_bar = ttk.Frame(panel)
        language_bar.pack(fill="x")
        ttk.Label(language_bar, text="Language / Idioma / Idioma").pack(side="left")
        self.language_choice = tk.StringVar(value=LANGUAGES.get(self.fields["language"].get(), "English"))
        language_menu = ttk.Combobox(language_bar, textvariable=self.language_choice,
                                     values=tuple(LANGUAGES.values()), state="readonly", width=15)
        language_menu.pack(side="left", padx=8)
        language_menu.bind("<<ComboboxSelected>>", self.change_language)
        tabs = ttk.Notebook(panel)
        tabs.pack(fill="x", pady=(0, 8))
        home = ttk.Frame(tabs, padding=8)
        settings = ttk.Frame(tabs, padding=8)
        advanced = ttk.Frame(tabs, padding=8)
        tabs.add(home, text="Mis herramientas")
        tabs.add(settings, text="Rutas y proyecto")
        tabs.add(advanced, text="Instalación y pruebas avanzadas")
        ttk.Label(home, text="Reutiliza tus herramientas. Compilar un proyecto no reconstruye GCC ni newlib.").pack(
            anchor="w")
        self.inventory = ttk.Treeview(home, columns=("name", "version", "status"), show="headings", height=8)
        for column, title, width in (("name", "Componente", 150), ("version", "Versión", 200),
                                     ("status", "Estado", 620)):
            self.inventory.heading(column, text=title)
            self.inventory.column(column, width=width, stretch=column == "status")
        self.inventory.pack(fill="x", pady=8)
        shortcuts = ttk.Frame(home)
        shortcuts.pack(fill="x")
        self.actions = []
        for index, (label, callback) in enumerate((("Detectar / comprobar", lambda: self.scan(False)),
                                ("Buscar actualizaciones", lambda: self.scan(True)),
                                ("Instalar / actualizar seleccionado", self.update_selected),
                                ("Compilar proyecto", lambda: self.start("project")),
                                ("Comprobar receta del port", lambda: self.start("project_check")),
                                ("Reconstruir solo SDK", lambda: self.start("sdk")))):
            button = ttk.Button(shortcuts, text=label, command=callback)
            button.grid(row=index // 3, column=index % 3, padx=3, pady=3, sticky="ew")
            self.actions.append(button)
        for column in range(3):
            shortcuts.columnconfigure(column, weight=1)
        grid = ttk.Frame(settings)
        grid.pack(fill="x")
        labels = (("msys", "MSYS2"), ("sdk", "Código de xSDK"), ("prefix", "Compilador instalado (carpeta raíz)"),
                  ("work", "Carpeta de trabajo"), ("glslang", "glslang.exe instalado (opcional)"),
                  ("project", "Proyecto CMake o raíz del port"), ("rom", "ROM privada del proyecto (opcional)"),
                  ("sdl", "SDL3_DIR (opcional)"),
                  ("build_type", "Configuración CMake"), ("cmake_args", "Opciones CMake (lista JSON)"),
                  ("target", "Prueba avanzada"), ("jobs", "Trabajos simultáneos"))
        for row, (key, label) in enumerate(labels):
            ttk.Label(grid, text=label).grid(row=row, column=0, sticky="w", pady=3)
            if key in ("build_type", "target"):
                choices = BUILD_TYPES if key == "build_type" else MAKE_TARGETS
                entry = ttk.Combobox(grid, textvariable=self.fields[key], values=choices, state="readonly")
            else:
                entry = ttk.Entry(grid, textvariable=self.fields[key])
            entry.grid(row=row, column=1, sticky="ew", padx=10)
            if key in ("msys", "sdk", "prefix", "work", "project", "sdl", "glslang", "rom"):
                ttk.Button(grid, text="Elegir…", command=lambda name=key: self.choose(name)).grid(row=row, column=2)
        ttk.Checkbutton(grid, text="Actualizar automáticamente al abrir (solo copias Git limpias)",
                        variable=self.fields["auto_update"], onvalue="1", offvalue="0",
                        command=self.save_preferences).grid(row=len(labels), column=1, sticky="w")
        ttk.Checkbutton(grid, text="Restaurar entradas heredadas locales (solo con permiso para usarlas)",
                        variable=self.fields["restore_inputs"], onvalue="1", offvalue="0").grid(
                            row=len(labels) + 1, column=1, sticky="w")
        grid.columnconfigure(1, weight=1)
        buttons = ttk.Frame(advanced)
        buttons.pack(fill="x", pady=12)
        for index, (label, action) in enumerate((("Diagnóstico", "diagnose"), ("1. Dependencias", "dependencies"),
                ("Construir compilador (lento)", "toolchain"), ("Construir shaders", "shaders"),
                ("4. Construir SDK", "sdk"),
                ("5. Ejemplos", "samples"), ("Compilar proyecto", "project"), ("Verificar herramientas", "validate"),
                ("Construir prueba avanzada", "advanced"), ("Actualizar código", "update"),
                ("Crear paquete portable", "bundle"))):
            button = ttk.Button(buttons, text=label, command=lambda name=action: self.start(name))
            button.grid(row=index // 4, column=index % 4, padx=3, pady=3, sticky="ew")
            self.actions.append(button)
        ttk.Button(buttons, text="Cancelar", command=self.cancel).grid(row=3, column=3, padx=3)
        for column in range(4):
            buttons.columnconfigure(column, weight=1)
        self.output = tk.Text(panel, wrap="word", font=("Consolas", 10), state="disabled")
        self.output.pack(fill="both", expand=True)
        bottom = ttk.Frame(panel)
        bottom.pack(fill="x", pady=(8, 0))
        ttk.Button(bottom, text="Abrir resultados", command=self.results).pack(side="left")
        ttk.Button(bottom, text="Abrir logs", command=self.logs).pack(side="left")
        ttk.Button(bottom, text="Créditos", command=lambda: self.info("Créditos", CREDITS)).pack(side="left")
        ttk.Label(panel, textvariable=self.status).pack(anchor="w", pady=(6, 0))
        self.apply_language()
        window.protocol("WM_DELETE_WINDOW", self.close)
        window.after(100, self.poll)
        window.after(200, lambda: self.scan(False))
        if self.fields["auto_update"].get() == "1":
            window.after(1500, self.auto_update)

    def tr(self, text):
        return translate(str(text), self.fields["language"].get())

    def info(self, title, body):
        return messagebox.showinfo(self.tr(title), self.tr(body))

    def error(self, title, body):
        return messagebox.showerror(self.tr(title), self.tr(body))

    def ask(self, title, body):
        return messagebox.askyesno(self.tr(title), self.tr(body))

    def change_language(self, event=None):
        code = next(key for key, label in LANGUAGES.items() if label == self.language_choice.get())
        self.fields["language"].set(code)
        self.apply_language()
        self.save_preferences()

    def apply_language(self):
        self.window.title(self.tr("xSDK para Windows — experimental"))
        def visit(widget):
            if "text" in widget.keys():
                widget.configure(text=self.tr(widget.cget("text")))
            if isinstance(widget, ttk.Notebook):
                for tab in widget.tabs():
                    widget.tab(tab, text=self.tr(widget.tab(tab, "text")))
            for child in widget.winfo_children():
                visit(child)
        visit(self.window)
        for column in ("name", "version", "status"):
            self.inventory.heading(column, text=self.tr(self.inventory.heading(column, "text")))
        for key in self.inventory.get_children():
            self.inventory.item(key, values=tuple(self.tr(value) for value in self.inventory.item(key, "values")))
        self.status.set(self.tr(self.status.get()))

    def auto_update(self):
        if self.busy:
            self.window.after(500, self.auto_update)
        else:
            self.start("update")

    def scan(self, online=False):
        if self.busy:
            return
        values = {key: value.get() for key, value in self.fields.items()}
        self.busy = True
        self.active_action = "Consultar actualizaciones" if online else "Detectar herramientas"
        self.started_at = time.monotonic()
        for button in self.actions:
            button.configure(state="disabled")
        threading.Thread(target=self.scan_worker, args=(values, online), daemon=True).start()

    def scan_worker(self, values, online):
        code = 0
        try:
            self.events.put(inspect(values, online))
        except Exception as error:
            code = 1
            self.events.put("No se pudo inspeccionar: " + str(error) + "\n")
        self.events.put((code, "Consulta sin compilación; vuelve a comprobar después de actualizar"))

    def update_selected(self):
        if self.busy:
            return
        selected = self.inventory.selection()
        if not selected:
            self.info("Componentes",
                      "Selecciona una fila para instalar o actualizar solo ese componente")
            return
        key = selected[0]
        if key in ("toolchain", "newlib", "cxx", "binutils"):
            if not self.ask("Actualizar compilador", "Esto reconstruye GCC y newlib y puede tardar bastante. "
                                      "Para usar tus herramientas actuales basta con indicar su ruta. "
                                      "¿Quieres construir un compilador nuevo sin reemplazar el existente?"):
                return
            destination = filedialog.asksaveasfilename(title=self.tr("Carpeta NUEVA del compilador"), initialfile="compiler-nuevo")
            if not destination:
                return
            if Path(destination).exists():
                self.error("Compilador", "Elige una ruta que todavía no exista")
                return
            self.fields["prefix"].set(destination)
            self.start("toolchain_fresh")
        elif key == "shaders":
            source = Path(self.fields["work"].get()) / "glslang/.git"
            self.start("shaders_update" if source.exists() else "shaders")
        elif key == "sdk":
            self.start("update")
        elif key == "dependencies":
            self.start("dependencies")

    def save_preferences(self):
        try:
            self.folder.mkdir(parents=True, exist_ok=True)
            values = {key: value.get() for key, value in self.fields.items()}
            self.settings_path.write_text(json.dumps(values, indent=2), encoding="utf-8")
        except OSError as error:
            self.error("Preferencias", str(error))

    def choose(self, key):
        folder = (filedialog.askopenfilename(filetypes=[(self.tr("Ejecutable"), "*.exe")])
                  if key == "glslang" else filedialog.askopenfilename(filetypes=[("ROM", "*.z64 *.n64 *.v64")])
                  if key == "rom" else filedialog.askdirectory())
        if folder:
            self.fields[key].set(folder)

    def start(self, action):
        if self.busy:
            return
        values = {key: value.get() for key, value in self.fields.items()}
        try:
            if action in ("project", "samples", "sdk", "validate"):
                if not (Path(values["prefix"]) / "bin/powerpc-xsdk-elf-g++.exe").is_file():
                    raise ValueError("Indica tu compilador existente en Rutas y proyecto, "
                                     "o instala el componente faltante")
            args, env = plan(action=action, **values)
            if not Path(args[0]).is_file():
                raise ValueError("Instala y actualiza MSYS2 desde https://www.msys2.org/ y elige su carpeta")
            if not (Path(values["sdk"]) / "tools/windows/run.sh").is_file():
                raise ValueError("La carpeta seleccionada no contiene este port de xSDK")
            self.folder.mkdir(parents=True, exist_ok=True)
            self.settings_path.write_text(json.dumps(values, indent=2), encoding="utf-8")
        except (OSError, ValueError) as error:
            self.error("Configuración", str(error))
            return
        self.cancelled.clear()
        self.busy = True
        self.active_action = action
        self.started_at = time.monotonic()
        for button in self.actions:
            button.configure(state="disabled")
        self.status.set(self.tr("Ejecutando: ") + action)
        threading.Thread(target=self.run, args=(args, env, action), daemon=True).start()

    def run(self, args, env, action):
        log_path = self.folder / (time.strftime("%Y%m%d-%H%M%S-") + action + ".log")
        code = -1
        try:
            with log_path.open("w", encoding="utf-8") as log:
                self.process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                env=env, encoding="utf-8", errors="replace",
                                                creationflags=subprocess.CREATE_NO_WINDOW)
                if self.cancelled.is_set():
                    self.cancel()
                for line in self.process.stdout:
                    log.write(line)
                    log.flush()
                    self.events.put(line)
                    if line.startswith("XSDK_NEW_ROOT="):
                        self.events.put({"paths": {"sdk": line.strip().split("=", 1)[1]}})
                code = self.process.wait()
        except OSError as error:
            self.events.put(str(error) + "\n")
            if self.process and self.process.poll() is None:
                self.cancel()
                self.process.wait()
        finally:
            self.process = None
            self.events.put((code, log_path))

    def poll(self):
        for _ in range(200):
            try:
                item = self.events.get_nowait()
            except queue.Empty:
                break
            if isinstance(item, dict):
                if "rows" in item:
                    for key in self.inventory.get_children():
                        self.inventory.delete(key)
                for row in item.get("rows", []):
                    self.inventory.insert("", "end", iid=row["key"],
                                          values=tuple(self.tr(row[key]) for key in ("name", "version", "status")))
                for key in ("prefix", "msys", "glslang", "sdk"):
                    if item.get("paths", {}).get(key):
                        self.fields[key].set(item["paths"][key])
                self.save_preferences()
            elif isinstance(item, tuple):
                code, log = item
                message = "Etapa terminada" if code == 0 else f"Error/cancelación ({code})"
                self.status.set(self.tr(message) + f" · Log: {log}")
                if code == 0 and self.active_action in ("shaders", "shaders_update"):
                    self.fields["glslang"].set(str(Path(self.fields["prefix"].get()) / "bin/glslang.exe"))
                    self.save_preferences()
                self.busy = False
                for button in self.actions:
                    button.configure(state="normal")
            else:
                self.output.configure(state="normal")
                self.output.insert("end", item)
                self.output.delete("1.0", "end-5000l")
                self.output.see("end")
                self.output.configure(state="disabled")
        if self.busy:
            elapsed = int(time.monotonic() - self.started_at)
            self.status.set(self.tr(f"Ejecutando: {self.active_action} · "
                                    f"{elapsed // 60:02d}:{elapsed % 60:02d} · Consulta los logs"))
        self.window.after(100, self.poll)

    def cancel(self):
        self.cancelled.set()
        process = self.process
        if process and process.poll() is None:
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def results(self):
        project = Path(self.fields["project"].get())
        folder = (Path(self.fields["work"].get()) / "projects" / project.name
                  if (project / "xsdk-project.json").is_file() else Path(self.fields["sdk"].get()) / "build")
        if folder.is_dir():
            os.startfile(folder)
        else:
            self.info("Resultados", "Los ejemplos todavía no están construidos")

    def logs(self):
        folder = Path(self.fields["work"].get()) / "toolchain/logs"
        try:
            self.folder.mkdir(parents=True, exist_ok=True)
            os.startfile(folder if folder.is_dir() else self.folder)
        except OSError as error:
            self.error("Logs", str(error))

    def close(self):
        if self.busy:
            self.info("Proceso activo", "Cancela la tarea o espera a que termine antes de cerrar")
        else:
            self.window.destroy()


if __name__ == "__main__":
    if os.name != "nt":
        raise SystemExit("La interfaz se ejecuta en Windows; las pruebas portables no necesitan abrirla")
    root = tk.Tk()
    App(root)
    root.mainloop()
