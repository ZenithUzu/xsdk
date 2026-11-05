"""Experimental Windows front-end for this fork of xenosworks/xsdk (MIT)."""
import json
import os
import queue
import subprocess
import sys
import threading
import time
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from processes import hidden_options
from build_plan import plan
from i18n import LANGUAGES, translate
from options import BUILD_TYPES, MAKE_TARGETS
from manager import inspect
from game_package import package_game
from settings import recover, legacy_profiles
from dependencies import DEFAULTS as SOURCE_DEFAULTS, SOURCE_FIELDS, dependency_plan, github_source

FROZEN = getattr(sys, "frozen", False)
ROOT = (Path(sys.executable).resolve().parent / "sdk" if FROZEN
        else Path(__file__).resolve().parents[2])
DEFAULT_SDK = Path("C:/xsdk-windows") if FROZEN and Path("C:/xsdk-windows").is_dir() else ROOT
CREDITS = """xSDK original: Mena / xenosworks — MIT
https://github.com/xenosworks/xsdk
Port experimental para Windows e interfaz: ZenithUzu, con asistencia de OpenAI Codex.
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
        self.folder = (Path(sys.executable).resolve().parent / "data" if FROZEN
                       else Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "xsdk-windows")
        self.settings_path = self.folder / "settings.json"
        defaults = {"msys": "C:/msys64", "sdk": str(DEFAULT_SDK),
                    "prefix": "C:/xsdk-tools/compiler", "work": "C:/xsdk-tools/work", "project": "", "jobs": "4",
                    "sdl": "C:/SDL-xenon/build-xsdk", "build_type": "Release",
                    "cmake_args": "[]", "target": "cmake_check",
                    "auto_update": "0", "glslang": "", "rom": "", "language": "en", "restore_inputs": "0",
                    "pc_game": "", "package_output": "", "include_mods": "0"}
        defaults.update(SOURCE_DEFAULTS)
        defaults, self.recovered_profiles = recover(defaults, self.settings_path)
        self.fields = {name: tk.StringVar(value=value) for name, value in defaults.items()}
        self.status = tk.StringVar(value="Port experimental — aún requiere validación completa en Windows")
        window.title("xSDK para Windows — experimental")
        window.geometry(f"{min(1180, window.winfo_screenwidth() - 80)}x"
                        f"{min(920, max(600, window.winfo_screenheight() - 100))}")
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
        sources = ttk.Frame(tabs, padding=8)
        tabs.add(sources, text="Fuentes y dependencias")
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
                                ("Reconstruir solo SDK", lambda: self.start("sdk")),
                                ("Construir y empaquetar juego", lambda: self.start("game_package")),
                                ("Empaquetar compilación existente", lambda: self.start("package_existing")))):
            button = ttk.Button(shortcuts, text=label, command=callback)
            button.grid(row=index // 3, column=index % 3, padx=3, pady=3, sticky="ew")
            self.actions.append(button)
        for column in range(3):
            shortcuts.columnconfigure(column, weight=1)
        settings_canvas = tk.Canvas(settings, height=350, highlightthickness=0)
        settings_scroll = ttk.Scrollbar(settings, orient="vertical", command=settings_canvas.yview)
        settings_scroll.pack(side="right", fill="y")
        settings_canvas.pack(side="left", fill="both", expand=True)
        settings_canvas.configure(yscrollcommand=settings_scroll.set)
        grid = ttk.Frame(settings_canvas)
        settings_item = settings_canvas.create_window((0, 0), window=grid, anchor="nw")
        grid.bind("<Configure>", lambda event: settings_canvas.configure(
            scrollregion=settings_canvas.bbox("all")))
        settings_canvas.bind("<Configure>", lambda event: settings_canvas.itemconfigure(
            settings_item, width=event.width))
        labels = (("msys", "MSYS2"), ("sdk", "Código de xSDK"), ("prefix", "Compilador instalado (carpeta raíz)"),
                  ("work", "Carpeta de trabajo"), ("glslang", "glslang.exe instalado (opcional)"),
                  ("project", "Proyecto CMake o raíz del port"), ("rom", "ROM privada del proyecto (opcional)"),
                  ("sdl", "SDL3_DIR (opcional)"),
                  ("pc_game", "CoopDX PC local (opcional)"),
                  ("package_output", "Carpeta NUEVA del juego empaquetado"),
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
            if key in ("msys", "sdk", "prefix", "work", "project", "sdl", "glslang", "rom",
                       "pc_game", "package_output"):
                ttk.Button(grid, text="Elegir…", command=lambda name=key: self.choose(name)).grid(row=row, column=2)
        ttk.Checkbutton(grid, text="Consultar actualizaciones al abrir (sin instalar)",
                        variable=self.fields["auto_update"], onvalue="1", offvalue="0",
                        command=self.save_preferences).grid(row=len(labels), column=1, sticky="w")
        ttk.Checkbutton(grid, text="Restaurar entradas heredadas locales (solo con permiso para usarlas)",
                        variable=self.fields["restore_inputs"], onvalue="1", offvalue="0").grid(
                            row=len(labels) + 1, column=1, sticky="w")
        ttk.Checkbutton(grid, text="Incluir mods y packs locales (compatibilidad sin confirmar)",
                        variable=self.fields["include_mods"], onvalue="1", offvalue="0").grid(
                            row=len(labels) + 2, column=1, sticky="w")
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
        source_canvas = tk.Canvas(sources, height=350, highlightthickness=0)
        source_scroll = ttk.Scrollbar(sources, orient="vertical", command=source_canvas.yview)
        source_scroll.pack(side="right", fill="y")
        source_canvas.pack(fill="both", expand=True)
        source_canvas.configure(yscrollcommand=source_scroll.set)
        source_grid = ttk.Frame(source_canvas)
        source_item = source_canvas.create_window((0, 0), window=source_grid, anchor="nw")
        source_grid.bind("<Configure>", lambda event: source_canvas.configure(scrollregion=source_canvas.bbox("all")))
        source_canvas.bind("<Configure>", lambda event: source_canvas.itemconfigure(source_item, width=event.width))
        source_labels = (("msys", "MSYS2"), ("sdk_repo", "Repositorio xSDK Windows (HTTPS GitHub)"),
                         ("sdk_ref", "Rama xSDK"), ("sdk", "Carpeta fuente xSDK"),
                         ("prefix", "Compilador instalado o destino NUEVO"),
                         ("shader_repo", "Repositorio glslang-xenon"), ("shader_ref", "Rama glslang"),
                         ("sdl_repo", "Repositorio SDL3 Xenon"), ("sdl_ref", "Rama SDL3"),
                         ("sdl_source", "Carpeta fuente SDL3"), ("sdl", "Carpeta compilada SDL3"),
                         ("work", "Carpeta de trabajo"), ("search_root", "Carpeta adicional para buscar herramientas"))
        for row, (key, label) in enumerate(source_labels):
            ttk.Label(source_grid, text=label).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Entry(source_grid, textvariable=self.fields[key]).grid(row=row, column=1, sticky="ew", padx=8)
            if key.endswith("_repo"):
                ttk.Button(source_grid, text="Abrir enlace", command=lambda name=key: self.open_source(name)).grid(
                    row=row, column=2)
            elif key not in ("sdk_ref", "sdl_ref", "shader_ref"):
                ttk.Button(source_grid, text="Elegir…", command=lambda name=key: self.choose(name)).grid(
                    row=row, column=2)
        source_grid.columnconfigure(1, weight=1)
        ttk.Label(source_grid, text=("MSYS2 trabaja por detrás. "
                                     "Las descargas y compilaciones solo empiezan al pulsar un botón."),
                  wraplength=850).grid(row=len(source_labels), column=0, columnspan=3, sticky="w", pady=8)
        dependency_buttons = (("Detectar rutas instaladas", lambda: self.scan(False)),
                              ("Recuperar rutas anteriores", self.recover_previous),
                              ("Descargar xSDK", lambda: self.start("deps_fetch_sdk")),
                              ("Descargar SDL3", lambda: self.start("deps_fetch_sdl")),
                              ("Construir xSDK", lambda: self.start("deps_build_sdk")),
                              ("Construir SDL3", lambda: self.start("deps_build_sdl")),
                              ("Preparar todo lo faltante", lambda: self.start("deps_prepare")),
                              ("Actualizar fuentes y reconstruir", lambda: self.start("deps_update_all")),
                              ("Construir compilador en destino nuevo", self.new_compiler),
                              ("Construir glslang", lambda: self.start("deps_build_shaders")))
        for index, (label, callback) in enumerate(dependency_buttons):
            button = ttk.Button(source_grid, text=label, command=callback)
            button.grid(row=len(source_labels) + 1 + index // 3, column=index % 3, sticky="ew", padx=3, pady=3)
            self.actions.append(button)
        ttk.Button(source_grid, text="Web de MSYS2", command=lambda: webbrowser.open("https://www.msys2.org/")).grid(
            row=len(source_labels) + 5, column=0, sticky="w")
        ttk.Button(source_grid, text="Ver receta del compilador", command=self.open_compiler_recipe).grid(
            row=len(source_labels) + 5, column=1, sticky="w")
        self.output = tk.Text(panel, wrap="word", font=("Consolas", 10), state="disabled")
        bottom = ttk.Frame(panel)
        bottom.pack(side="bottom", fill="x", pady=(8, 0))
        ttk.Button(bottom, text="Abrir resultados", command=self.results).pack(side="left")
        ttk.Button(bottom, text="Abrir logs", command=self.logs).pack(side="left")
        ttk.Button(bottom, text="Créditos", command=lambda: self.info("Créditos", CREDITS)).pack(side="left")
        ttk.Button(bottom, text="Cancelar", command=self.cancel).pack(side="left")
        ttk.Label(panel, textvariable=self.status).pack(side="bottom", anchor="w", pady=(6, 0))
        self.output.pack(fill="both", expand=True)
        self.apply_language()
        self.write_output(self.tr("Listo. La información y el progreso aparecerán aquí.") + "\n")
        if self.settings_path.is_file():
            self.write_output(self.tr("Configuración cargada: ") + str(self.settings_path) + "\n")
        for profile, keys in self.recovered_profiles:
            self.write_output(self.tr("Rutas recuperadas de: ") + profile + " · " + ", ".join(keys) + "\n")
        window.protocol("WM_DELETE_WINDOW", self.close)
        window.after(100, self.poll)
        window.after(200, lambda: self.scan(False))
        if self.fields["auto_update"].get() == "1" and "--startup-test" not in sys.argv:
            window.after(1500, self.auto_update)

    def write_output(self, text):
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.delete("1.0", "end-5000l")
        self.output.see("end")
        self.output.configure(state="disabled")

    def recover_previous(self):
        if self.busy:
            return
        values = {key: value.get() for key, value in self.fields.items()}
        # Recover invalid/empty paths only when explicitly requested; preserve valid choices.
        profiles = legacy_profiles(self.settings_path)
        values, origins = recover(values, self.settings_path, candidates=profiles, replace_invalid=True,
                                  saved_override=values)
        for key, value in values.items():
            self.fields[key].set(value)
        self.language_choice.set(LANGUAGES.get(self.fields["language"].get(), "English"))
        self.apply_language()
        if not origins:
            self.write_output(self.tr("No se encontraron rutas anteriores adicionales.") + "\n")
        for profile, keys in origins:
            self.write_output(self.tr("Rutas recuperadas de: ") + profile + " · " + ", ".join(keys) + "\n")
        self.save_preferences()
        self.scan(False)

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
            self.scan(True)

    def scan(self, online=False):
        if self.busy:
            return
        values = {key: value.get() for key, value in self.fields.items()}
        self.busy = True
        self.active_action = "Consultar actualizaciones" if online else "Detectar herramientas"
        self.started_at = time.monotonic()
        self.last_progress_notice = self.started_at
        self.write_output("\n[" + time.strftime("%H:%M:%S") + "] " + self.tr("Iniciando: ") +
                          self.tr(self.active_action) + "\n")
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
            destination = filedialog.asksaveasfilename(title=self.tr("Carpeta NUEVA del compilador"),
                                                     initialfile="compiler-nuevo")
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

    def new_compiler(self):
        if self.busy:
            return
        if Path(self.fields["prefix"].get()).exists():
            parent = filedialog.askdirectory(title=self.tr("Carpeta NUEVA del compilador"))
            if not parent:
                return
            self.fields["prefix"].set(str(Path(parent) / ("compiler-" + time.strftime("%Y%m%d-%H%M%S"))))
        self.start("deps_build_compiler")

    def open_compiler_recipe(self):
        try:
            url, ref = github_source(self.fields["sdk_repo"].get(), self.fields["sdk_ref"].get())
            webbrowser.open(url.removesuffix(".git") + "/blob/" + ref + "/tools/toolchain/build.sh")
        except ValueError as error:
            self.error("Configuración", str(error))

    def open_source(self, key):
        branch = {"sdk_repo": "sdk_ref", "sdl_repo": "sdl_ref", "shader_repo": "shader_ref"}[key]
        try:
            url, ref = github_source(self.fields[key].get(), self.fields[branch].get())
            webbrowser.open(url.removesuffix(".git") + "/tree/" + ref)
        except ValueError as error:
            self.error("Configuración", str(error))

    def choose(self, key):
        if key == "package_output":
            parent = filedialog.askdirectory()
            if parent:
                self.fields[key].set(str(Path(parent) / ("sm64coopdx360-" + time.strftime("%Y%m%d-%H%M%S"))))
            return
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
            if action in ("game_package", "package_existing"):
                if not values["package_output"]:
                    raise ValueError("Choose a NEW game output folder in Paths and project.")
                if Path(values["package_output"]).exists():
                    raise ValueError("Choose a NEW output folder; existing folders are never overwritten.")
                if not (Path(values["project"]) / "xsdk-project.json").is_file():
                    raise ValueError("Select the CoopDX repository root containing xsdk-project.json.")
            build_values = {key: value for key, value in values.items()
                            if key not in ("pc_game", "package_output", "include_mods", *SOURCE_FIELDS)}
            planned = ("project_check" if action == "package_existing" else
                       "project" if action == "game_package" else action)
            if action.startswith("deps_"):
                args, env = dependency_plan(action.removeprefix("deps_"), values, ROOT)
            else:
                args, env = plan(action=planned, **build_values)
            if not Path(args[0]).is_file():
                raise ValueError("Instala y actualiza MSYS2 desde https://www.msys2.org/ y elige su carpeta")
            if not action.startswith("deps_") and not (Path(values["sdk"]) / "tools/windows/run.sh").is_file():
                raise ValueError("La carpeta seleccionada no contiene este port de xSDK")
            self.folder.mkdir(parents=True, exist_ok=True)
            self.settings_path.write_text(json.dumps(values, indent=2), encoding="utf-8")
        except (OSError, ValueError) as error:
            self.write_output(self.tr("Configuración") + ": " + self.tr(str(error)) + "\n")
            self.error("Configuración", str(error))
            return
        self.cancelled.clear()
        self.busy = True
        self.active_action = action
        self.started_at = time.monotonic()
        self.last_progress_notice = self.started_at
        self.write_output("\n[" + time.strftime("%H:%M:%S") + "] " + self.tr("Iniciando: ") +
                          self.tr(self.active_action) + "\n")
        for button in self.actions:
            button.configure(state="disabled")
        self.status.set(self.tr("Ejecutando: ") + action)
        threading.Thread(target=self.run, args=(args, env, action, values), daemon=True).start()

    def run(self, args, env, action, values):
        log_path = self.folder / (time.strftime("%Y%m%d-%H%M%S-") + action + ".log")
        code = -1
        try:
            with log_path.open("w", encoding="utf-8") as log:
                self.process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                env=env, encoding="utf-8", errors="replace", **hidden_options())
                if self.cancelled.is_set():
                    self.cancel()
                for line in self.process.stdout:
                    log.write(line)
                    log.flush()
                    self.events.put(line)
                    if line.startswith("XSDK_PATHS="):
                        self.events.put({"paths": json.loads(line.strip().split("=", 1)[1])})
                    if line.startswith("XSDK_NEW_ROOT="):
                        self.events.put({"paths": {"sdk": line.strip().split("=", 1)[1]}})
                code = self.process.wait()
                if code == 0 and action in ("game_package", "package_existing"):
                    destination, count = package_game(
                        values["project"], Path(values["work"]) / "projects" / Path(values["project"]).name,
                        values["package_output"], values["pc_game"], values["include_mods"] == "1",
                        self.cancelled.is_set)
                    message = f"Package ready: {destination} ({count} files). Hardware validation: not-run.\n"
                    log.write(message)
                    self.events.put(message)
        except (OSError, ValueError) as error:
            code = 1
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
                    self.write_output(self.tr(row["name"]) + " · " + row["version"] + " · " +
                                      self.tr(row["status"]) + (" · " + row["path"] if row.get("path") else "") + "\n")
                    self.inventory.insert("", "end", iid=row["key"],
                                          values=tuple(self.tr(row[key]) for key in ("name", "version", "status")))
                for key in ("prefix", "msys", "glslang", "sdk", "sdl", "sdl_source"):
                    if item.get("paths", {}).get(key):
                        self.fields[key].set(item["paths"][key])
                        if "rows" not in item:
                            self.write_output(self.tr("Ruta seleccionada: ") + key + " = " + item["paths"][key] + "\n")
                self.save_preferences()
            elif isinstance(item, tuple):
                code, log = item
                message = "Etapa terminada" if code == 0 else f"Error/cancelación ({code})"
                self.status.set(self.tr(message) + f" · Log: {log}")
                elapsed = int(time.monotonic() - self.started_at)
                self.write_output(self.tr(message) + f" · {elapsed // 60:02d}:{elapsed % 60:02d} · Log: {log}\n")
                if code == 0 and self.active_action in ("shaders", "shaders_update"):
                    self.fields["glslang"].set(str(Path(self.fields["prefix"].get()) / "bin/glslang.exe"))
                    self.save_preferences()
                self.busy = False
                if code == 0 and self.active_action.startswith("deps_"):
                    self.window.after(250, lambda: self.scan(False))
                for button in self.actions:
                    button.configure(state="normal")
            else:
                self.write_output(item)
        if self.busy:
            elapsed = int(time.monotonic() - self.started_at)
            if time.monotonic() - getattr(self, "last_progress_notice", self.started_at) >= 15:
                self.write_output(self.tr("Sigue en ejecución: ") + self.tr(self.active_action) +
                                  f" · {elapsed // 60:02d}:{elapsed % 60:02d}\n")
                self.last_progress_notice = time.monotonic()
            self.status.set(self.tr(f"Ejecutando: {self.active_action} · "
                                    f"{elapsed // 60:02d}:{elapsed % 60:02d} · Consulta los logs"))
        self.window.after(100, self.poll)

    def cancel(self):
        self.cancelled.set()
        if self.busy:
            self.write_output(self.tr("Cancelación solicitada.") + "\n")
        process = self.process
        if process and process.poll() is None:
            subprocess.run([str(Path(os.environ.get("SystemRoot", "C:/Windows")) / "System32/taskkill.exe"),
                            "/PID", str(process.pid), "/T", "/F"], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **hidden_options())

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


def main():
    if os.name != "nt":
        raise SystemExit("The desktop interface runs on Windows.")
    root = tk.Tk()
    if len(sys.argv) == 3 and sys.argv[1] == "--startup-test":
        import manager
        root.withdraw()
        commands = []
        original = manager.command
        def recorded(args, env=None):
            commands.append([str(arg) for arg in args])
            return original(args, env)
        manager.command = recorded
        app = App(root)
        app.fields["auto_update"].set("0")
        app.save_preferences = lambda: None
        deadline = time.monotonic() + 60
        def finish():
            if not app.busy and app.inventory.get_children():
                forbidden = {"fetch", "clone", "merge", "ls-remote", "install"}
                passed = not any(forbidden.intersection(command) for command in commands)
                result = {"passed": passed, "frozen": FROZEN, "command_count": len(commands),
                          "commands": commands, "inventory_rows": len(app.inventory.get_children()),
                          "startup_network": False, "startup_installs": False}
                Path(sys.argv[2]).write_text(json.dumps(result, indent=2), encoding="utf-8")
                root.destroy()
            elif time.monotonic() > deadline:
                Path(sys.argv[2]).write_text('{"passed": false, "timeout": true}', encoding="utf-8")
                root.destroy()
            else:
                root.after(100, finish)
        root.after(300, finish)
        root.mainloop()
    elif len(sys.argv) == 3 and sys.argv[1] == "--self-test":
        root.withdraw()
        root.after = lambda *args: None
        app = App(root)
        app.save_preferences = lambda: None
        tested = []
        for code, label in LANGUAGES.items():
            app.language_choice.set(label)
            app.change_language()
            assert root.title() == translate("xSDK para Windows — experimental", code)
            tested.append(code)
        root.update_idletasks()
        result = {"passed": True, "frozen": FROZEN, "languages": tested,
                  "tk": str(tk.TkVersion), "python": sys.version.split()[0]}
        Path(sys.argv[2]).write_text(json.dumps(result, indent=2), encoding="utf-8")
        root.destroy()
    else:
        App(root)
        root.mainloop()


if __name__ == "__main__":
    main()
