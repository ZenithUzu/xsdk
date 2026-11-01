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
from options import BUILD_TYPES, MAKE_TARGETS

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
                    "sdl": "", "build_type": "Release", "cmake_args": "[]", "target": "cmake_check", "auto_update": "0"}
        try:
            saved = json.loads(self.settings_path.read_text(encoding="utf-8"))
            defaults.update({key: str(value) for key, value in saved.items() if key in defaults})
        except (OSError, ValueError, AttributeError):
            pass
        self.fields = {name: tk.StringVar(value=value) for name, value in defaults.items()}
        self.status = tk.StringVar(value="Port experimental — aún requiere validación completa en Windows")
        window.title("xSDK para Windows — experimental")
        window.geometry("1100x900")
        panel = ttk.Frame(window, padding=14)
        panel.pack(fill="both", expand=True)
        ttk.Label(panel, text="xSDK · Windows", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(panel, text="Compilador PowerPC, shaders y ejemplos · sin Debian ni WSL").pack(
            anchor="w", pady=(0, 12))
        grid = ttk.Frame(panel)
        grid.pack(fill="x")
        labels = (("msys", "MSYS2"), ("sdk", "Código de xSDK"), ("prefix", "Instalar compilador en"),
                  ("work", "Carpeta de trabajo"), ("project", "Proyecto CMake"), ("sdl", "SDL3_DIR (opcional)"),
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
            if key in ("msys", "sdk", "prefix", "work", "project", "sdl"):
                ttk.Button(grid, text="Elegir…", command=lambda name=key: self.choose(name)).grid(row=row, column=2)
        ttk.Checkbutton(grid, text="Actualizar automáticamente al abrir (solo copias Git limpias)",
                        variable=self.fields["auto_update"], onvalue="1", offvalue="0",
                        command=self.save_preferences).grid(row=len(labels), column=1, sticky="w")
        grid.columnconfigure(1, weight=1)
        buttons = ttk.Frame(panel)
        buttons.pack(fill="x", pady=12)
        self.actions = []
        for index, (label, action) in enumerate((("Diagnóstico", "diagnose"), ("1. Dependencias", "dependencies"),
                ("2. Compilador", "toolchain"), ("3. Shaders", "shaders"), ("4. Construir SDK", "sdk"),
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
        ttk.Button(bottom, text="Créditos", command=lambda: messagebox.showinfo("Créditos", CREDITS)).pack(side="left")
        ttk.Label(panel, textvariable=self.status).pack(anchor="w", pady=(6, 0))
        window.protocol("WM_DELETE_WINDOW", self.close)
        window.after(100, self.poll)
        if self.fields["auto_update"].get() == "1":
            window.after(500, lambda: self.start("update"))

    def save_preferences(self):
        try:
            self.folder.mkdir(parents=True, exist_ok=True)
            values = {key: value.get() for key, value in self.fields.items()}
            self.settings_path.write_text(json.dumps(values, indent=2), encoding="utf-8")
        except OSError as error:
            messagebox.showerror("Preferencias", str(error))

    def choose(self, key):
        folder = filedialog.askdirectory()
        if folder:
            self.fields[key].set(folder)

    def start(self, action):
        if self.busy:
            return
        values = {key: value.get() for key, value in self.fields.items()}
        try:
            args, env = plan(action=action, **values)
            if not Path(args[0]).is_file():
                raise ValueError("Instala y actualiza MSYS2 desde https://www.msys2.org/ y elige su carpeta")
            if not (Path(values["sdk"]) / "tools/windows/run.sh").is_file():
                raise ValueError("La carpeta seleccionada no contiene este port de xSDK")
            self.folder.mkdir(parents=True, exist_ok=True)
            self.settings_path.write_text(json.dumps(values, indent=2), encoding="utf-8")
        except (OSError, ValueError) as error:
            messagebox.showerror("Configuración", str(error))
            return
        self.cancelled.clear()
        self.busy = True
        self.active_action = action
        self.started_at = time.monotonic()
        for button in self.actions:
            button.configure(state="disabled")
        self.status.set("Ejecutando: " + action)
        threading.Thread(target=self.run, args=(args, env, action), daemon=True).start()

    def run(self, args, env, action):
        log_path = self.folder / (time.strftime("%Y%m%d-%H%M%S-") + action + ".log")
        code = -1
        try:
            with log_path.open("w", encoding="utf-8") as log:
                self.process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                env=env, encoding="utf-8", errors="replace")
                if self.cancelled.is_set():
                    self.cancel()
                for line in self.process.stdout:
                    log.write(line)
                    log.flush()
                    self.events.put(line)
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
            if isinstance(item, tuple):
                code, log = item
                self.status.set(("Etapa terminada" if code == 0 else f"Error/cancelación ({code})") + f" · Log: {log}")
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
            self.status.set(f"Ejecutando: {self.active_action} · {elapsed // 60:02d}:{elapsed % 60:02d} · Consulta los logs")
        self.window.after(100, self.poll)

    def cancel(self):
        self.cancelled.set()
        process = self.process
        if process and process.poll() is None:
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def results(self):
        folder = Path(self.fields["sdk"].get()) / "build"
        if folder.is_dir():
            os.startfile(folder)
        else:
            messagebox.showinfo("Resultados", "Los ejemplos todavía no están construidos")

    def logs(self):
        folder = Path(self.fields["work"].get()) / "toolchain/logs"
        try:
            self.folder.mkdir(parents=True, exist_ok=True)
            os.startfile(folder if folder.is_dir() else self.folder)
        except OSError as error:
            messagebox.showerror("Logs", str(error))

    def close(self):
        if self.busy:
            messagebox.showinfo("Proceso activo", "Cancela la tarea o espera a que termine antes de cerrar")
        else:
            self.window.destroy()


if __name__ == "__main__":
    if os.name != "nt":
        raise SystemExit("La interfaz se ejecuta en Windows; las pruebas portables no necesitan abrirla")
    root = tk.Tk()
    App(root)
    root.mainloop()
