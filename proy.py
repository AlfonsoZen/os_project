import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, simpledialog

class PlanificadorProcesos:
    def __init__(self):
        self.procesos = []

    def agregar_proceso(self, id_proceso, tiempo_ejecucion, prioridad):
        self.procesos.append({"id": id_proceso, "tiempo": tiempo_ejecucion, "prioridad": prioridad})

    def calcular_estadisticas(self, tiempos_finalizacion):
        n = len(self.procesos)
        tiempos_espera = [tiempos_finalizacion[i] - self.procesos[i]['tiempo'] for i in range(n)]
        tiempo_promedio_espera = sum(tiempos_espera) / n
        tiempo_promedio_retorno = sum(tiempos_finalizacion) / n

        return {
            "tiempo_promedio_espera": tiempo_promedio_espera,
            "tiempo_promedio_retorno": tiempo_promedio_retorno
        }

    def ejecutar_fifo(self):
        tiempo_actual = 0
        tiempos_finalizacion = []
        log = "Ejecución FIFO:\n"

        for proceso in self.procesos:
            log += f"Ejecutando proceso {proceso['id']} (tiempo: {proceso['tiempo']})\n"
            tiempo_actual += proceso['tiempo']
            tiempos_finalizacion.append(tiempo_actual)

        estadisticas = self.calcular_estadisticas(tiempos_finalizacion)
        log += "\nEstadísticas:\n"
        log += f"Tiempo promedio de espera: {estadisticas['tiempo_promedio_espera']:.2f}\n"
        log += f"Tiempo promedio de retorno: {estadisticas['tiempo_promedio_retorno']:.2f}\n"

        return log

    def ejecutar_sjf(self):
        procesos_ordenados = sorted(self.procesos, key=lambda x: x['tiempo'])
        tiempo_actual = 0
        tiempos_finalizacion = []
        log = "Ejecución SJF:\n"

        for proceso in procesos_ordenados:
            log += f"Ejecutando proceso {proceso['id']} (tiempo: {proceso['tiempo']})\n"
            tiempo_actual += proceso['tiempo']
            tiempos_finalizacion.append(tiempo_actual)

        estadisticas = self.calcular_estadisticas(tiempos_finalizacion)
        log += "\nEstadísticas:\n"
        log += f"Tiempo promedio de espera: {estadisticas['tiempo_promedio_espera']:.2f}\n"
        log += f"Tiempo promedio de retorno: {estadisticas['tiempo_promedio_retorno']:.2f}\n"

        return log

    def ejecutar_round_robin(self, quantum):
        cola = self.procesos.copy()
        tiempo_actual = 0
        tiempos_finalizacion = {proceso['id']: 0 for proceso in self.procesos}
        tiempos_restantes = {proceso['id']: proceso['tiempo'] for proceso in self.procesos}
        log = "Ejecución Round Robin:\n"

        while cola:
            proceso = cola.pop(0)
            if tiempos_restantes[proceso['id']] > quantum:
                log += f"Ejecutando proceso {proceso['id']} (restante: {tiempos_restantes[proceso['id']]})\n"
                tiempo_actual += quantum
                tiempos_restantes[proceso['id']] -= quantum
                cola.append(proceso)
            else:
                log += f"Ejecutando proceso {proceso['id']} (restante: {tiempos_restantes[proceso['id']]})\n"
                tiempo_actual += tiempos_restantes[proceso['id']]
                tiempos_restantes[proceso['id']] = 0
                tiempos_finalizacion[proceso['id']] = tiempo_actual

        tiempos_finalizacion_list = [tiempos_finalizacion[proceso['id']] for proceso in self.procesos]
        estadisticas = self.calcular_estadisticas(tiempos_finalizacion_list)
        log += "\nEstadísticas:\n"
        log += f"Tiempo promedio de espera: {estadisticas['tiempo_promedio_espera']:.2f}\n"
        log += f"Tiempo promedio de retorno: {estadisticas['tiempo_promedio_retorno']:.2f}\n"

        return log
class AdministradorMemoria:
    def __init__(self, tamano_memoria):
        self.tamano = tamano_memoria
        self.memoria = [-1] * tamano_memoria
        self.tabla_paginas = {}

    def cargar_proceso(self, id_proceso, tamano_proceso):
        paginas_necesarias = (tamano_proceso + self.tamano - 1) // self.tamano
        paginas = []
        for i in range(len(self.memoria)):
            if len(paginas) == paginas_necesarias:
                break
            if self.memoria[i] == -1:
                self.memoria[i] = id_proceso
                paginas.append(i)
        if len(paginas) < paginas_necesarias:
            return None
        self.tabla_paginas[id_proceso] = paginas
        return paginas

    def mostrar_estado(self):
        return {
            "memoria": self.memoria,
            "tabla_paginas": self.tabla_paginas
        }

    def reemplazo_fifo(self, id_proceso, tamano_proceso):
        paginas_necesarias = (tamano_proceso + self.tamano - 1) // self.tamano
        reemplazos = 0
        for i in range(len(self.memoria)):
            if reemplazos == paginas_necesarias:
                break
            if self.memoria[i] != -1:
                self.memoria[i] = id_proceso
                reemplazos += 1
        if reemplazos < paginas_necesarias:
            return None
        self.tabla_paginas[id_proceso] = [i for i, x in enumerate(self.memoria) if x == id_proceso]
        return self.tabla_paginas[id_proceso]


class SistemaArchivos:
    def __init__(self):
        self.directorio_actual = "raiz"
        self.sistema = {"raiz": {}}

    def mkdir(self, nombre):
        if nombre in self.sistema[self.directorio_actual]:
            return False
        self.sistema[self.directorio_actual][nombre] = {}
        return True

    def touch(self, nombre, contenido=""):
        if nombre in self.sistema[self.directorio_actual]:
            return False
        self.sistema[self.directorio_actual][nombre] = contenido
        return True

    def ls(self):
        return list(self.sistema[self.directorio_actual].keys())

    def rm(self, nombre):
        if nombre not in self.sistema[self.directorio_actual]:
            return False
        del self.sistema[self.directorio_actual][nombre]
        return True

    def leer_archivo(self, nombre):
        if nombre not in self.sistema[self.directorio_actual]:
            return None
        return self.sistema[self.directorio_actual][nombre]

    def escribir_archivo(self, nombre, contenido):
        if nombre not in self.sistema[self.directorio_actual]:
            return False
        self.sistema[self.directorio_actual][nombre] = contenido
        return True


class SistemaOperativoSimulador:
    def __init__(self):
        self.planificador = PlanificadorProcesos()
        self.administrador_memoria = AdministradorMemoria(10)
        self.sistema_archivos = SistemaArchivos()

    def crear_interfaz(self):
        self.root = tk.Tk()
        self.root.title("Simulador de Sistema Operativo")
        self.root.geometry("600x700")

        # Pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        # Pestaña de Planificación de Procesos
        frame_procesos = tk.Frame(self.notebook)
        self.notebook.add(frame_procesos, text="Planificación Procesos")
        self._crear_interfaz_procesos(frame_procesos)

        # Pestaña de Administración de Memoria
        frame_memoria = tk.Frame(self.notebook)
        self.notebook.add(frame_memoria, text="Administración Memoria")
        self._crear_interfaz_memoria(frame_memoria)

        # Pestaña de Sistema de Archivos
        frame_archivos = tk.Frame(self.notebook)
        self.notebook.add(frame_archivos, text="Sistema de Archivos")
        self._crear_interfaz_archivos(frame_archivos)

        self.root.mainloop()

    def _crear_interfaz_procesos(self, frame):
        tk.Label(frame, text="Planificación de Procesos", font=('Arial', 14)).pack(pady=10)

        frame_entrada = tk.Frame(frame)
        frame_entrada.pack(pady=10)

        tk.Label(frame_entrada, text="ID Proceso:").grid(row=0, column=0)
        self.id_proceso_entry = tk.Entry(frame_entrada)
        self.id_proceso_entry.grid(row=0, column=1)

        tk.Label(frame_entrada, text="Tiempo Ejecución:").grid(row=1, column=0)
        self.tiempo_entry = tk.Entry(frame_entrada)
        self.tiempo_entry.grid(row=1, column=1)

        tk.Label(frame_entrada, text="Prioridad:").grid(row=2, column=0)
        self.prioridad_entry = tk.Entry(frame_entrada)
        self.prioridad_entry.grid(row=2, column=1)

        tk.Button(frame, text="Agregar Proceso", command=self._agregar_proceso).pack(pady=5)

        frame_algoritmos = tk.Frame(frame)
        frame_algoritmos.pack(pady=10)

        tk.Button(frame_algoritmos, text="FIFO", command=self._ejecutar_fifo).grid(row=0, column=0, padx=5)
        tk.Button(frame_algoritmos, text="SJF", command=self._ejecutar_sjf).grid(row=0, column=1, padx=5)

        frame_rr = tk.Frame(frame)
        frame_rr.pack(pady=5)
        tk.Label(frame_rr, text="Quantum:").grid(row=0, column=0)
        self.quantum_entry = tk.Entry(frame_rr)
        self.quantum_entry.grid(row=0, column=1)
        tk.Button(frame_rr, text="Round Robin", command=self._ejecutar_round_robin).grid(row=0, column=2)

        self.resultado_procesos = tk.Text(frame, height=20, width=70)
        self.resultado_procesos.pack(pady=10)

    def _crear_interfaz_memoria(self, frame):
        tk.Label(frame, text="Administración de Memoria", font=('Arial', 14)).pack(pady=10)

        frame_entrada = tk.Frame(frame)
        frame_entrada.pack(pady=10)

        tk.Label(frame_entrada, text="ID Proceso:").grid(row=0, column=0)
        self.id_proceso_memoria_entry = tk.Entry(frame_entrada)
        self.id_proceso_memoria_entry.grid(row=0, column=1)

        tk.Label(frame_entrada, text="Tamaño Proceso:").grid(row=1, column=0)
        self.tamano_proceso_entry = tk.Entry(frame_entrada)
        self.tamano_proceso_entry.grid(row=1, column=1)

        tk.Button(frame, text="Cargar Proceso", command=self._cargar_proceso_memoria).pack(pady=5)
        tk.Button(frame, text="Reemplazo FIFO", command=self._reemplazo_fifo).pack(pady=5)
        tk.Button(frame, text="Mostrar Estado", command=self._mostrar_estado_memoria).pack(pady=5)

        self.resultado_memoria = tk.Text(frame, height=10, width=70)
        self.resultado_memoria.pack(pady=10)

    def _crear_interfaz_archivos(self, frame):
        tk.Label(frame, text="Sistema de Archivos", font=('Arial', 14)).pack(pady=10)

        frame_entrada = tk.Frame(frame)
        frame_entrada.pack(pady=10)

        tk.Label(frame_entrada, text="Nombre:").grid(row=0, column=0)
        self.nombre_archivo_entry = tk.Entry(frame_entrada)
        self.nombre_archivo_entry.grid(row=0, column=1)

        tk.Label(frame_entrada, text="Contenido:").grid(row=1, column=0)
        self.contenido_archivo_entry = tk.Entry(frame_entrada)
        self.contenido_archivo_entry.grid(row=1, column=1)

        tk.Button(frame, text="Crear Directorio", command=self._crear_directorio).pack(pady=5)
        tk.Button(frame, text="Crear Archivo", command=self._crear_archivo).pack(pady=5)
        tk.Button(frame, text="Listar Contenido", command=self._listar_contenido).pack(pady=5)
        tk.Button(frame, text="Eliminar", command=self._eliminar_archivo).pack(pady=5)
        tk.Button(frame, text="Leer Archivo", command=self._leer_archivo).pack(pady=5)
        tk.Button(frame, text="Escribir Archivo", command=self._escribir_archivo).pack(pady=5)

        self.resultado_archivos = tk.Text(frame, height=10, width=70)
        self.resultado_archivos.pack(pady=10)

    # Métodos de Procesos
    def _agregar_proceso(self):
        try:
            id_proceso = self.id_proceso_entry.get()
            tiempo = int(self.tiempo_entry.get())
            prioridad = int(self.prioridad_entry.get())
            self.planificador.agregar_proceso(id_proceso, tiempo, prioridad)
            messagebox.showinfo("Proceso Agregado", f"Proceso {id_proceso} agregado exitosamente")
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores válidos para tiempo y prioridad")

    def _ejecutar_fifo(self):
        log = self.planificador.ejecutar_fifo()
        self._mostrar_resultado_procesos(log)

    def _ejecutar_sjf(self):
        log = self.planificador.ejecutar_sjf()
        self._mostrar_resultado_procesos(log)

    def _ejecutar_round_robin(self):
        try:
            quantum = int(self.quantum_entry.get())
            log = self.planificador.ejecutar_round_robin(quantum)
            self._mostrar_resultado_procesos(log)
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor válido para el quantum")


    def _mostrar_resultado_procesos(self, log):
        self.resultado_procesos.delete(1.0, tk.END)
        self.resultado_procesos.insert(tk.END, log)

    # Métodos de Memoria
    def _cargar_proceso_memoria(self):
        try:
            id_proceso = self.id_proceso_memoria_entry.get()
            tamano_proceso = int(self.tamano_proceso_entry.get())
            paginas = self.administrador_memoria.cargar_proceso(id_proceso, tamano_proceso)

            if paginas:
                messagebox.showinfo("Proceso Cargado", f"Proceso {id_proceso} cargado en páginas: {paginas}")
            else:
                messagebox.showerror("Error", f"Memoria insuficiente para el proceso {id_proceso}")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor válido para el tamaño del proceso")

    def _reemplazo_fifo(self):
        try:
            id_proceso = self.id_proceso_memoria_entry.get()
            tamano_proceso = int(self.tamano_proceso_entry.get())
            paginas = self.administrador_memoria.reemplazo_fifo(id_proceso, tamano_proceso)

            if paginas:
                messagebox.showinfo("Proceso Reemplazado", f"Proceso {id_proceso} reemplazado en páginas: {paginas}")
            else:
                messagebox.showerror("Error", f"Memoria insuficiente para reemplazar el proceso {id_proceso}")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor válido para el tamaño del proceso")

    def _mostrar_estado_memoria(self):
        estado = self.administrador_memoria.mostrar_estado()
        self.resultado_memoria.delete(1.0, tk.END)
        self.resultado_memoria.insert(tk.END, f"Memoria: {estado['memoria']}\n")
        self.resultado_memoria.insert(tk.END, f"Tabla de Páginas: {estado['tabla_paginas']}")

    # Métodos de Sistema de Archivos
    def _crear_directorio(self):
        nombre = self.nombre_archivo_entry.get()
        if self.sistema_archivos.mkdir(nombre):
            messagebox.showinfo("Directorio Creado", f"Directorio '{nombre}' creado exitosamente")
        else:
            messagebox.showerror("Error", f"El directorio '{nombre}' ya existe")

    def _crear_archivo(self):
        nombre = self.nombre_archivo_entry.get()
        contenido = self.contenido_archivo_entry.get()
        if self.sistema_archivos.touch(nombre, contenido):
            messagebox.showinfo("Archivo Creado", f"Archivo '{nombre}' creado exitosamente")
        else:
            messagebox.showerror("Error", f"El archivo '{nombre}' ya existe")

    def _listar_contenido(self):
        contenido = self.sistema_archivos.ls()
        self.resultado_archivos.delete(1.0, tk.END)
        self.resultado_archivos.insert(tk.END, f"Contenido: {contenido}")

    def _eliminar_archivo(self):
        nombre = self.nombre_archivo_entry.get()
        if self.sistema_archivos.rm(nombre):
            messagebox.showinfo("Archivo Eliminado", f"'{nombre}' eliminado exitosamente")
        else:
            messagebox.showerror("Error", f"'{nombre}' no existe")

    def _leer_archivo(self):
        nombre = self.nombre_archivo_entry.get()
        contenido = self.sistema_archivos.leer_archivo(nombre)
        if contenido is not None:
            self.resultado_archivos.delete(1.0, tk.END)
            self.resultado_archivos.insert(tk.END, f"Contenido de '{nombre}': {contenido}")
        else:
            messagebox.showerror("Error", f"El archivo '{nombre}' no existe")

    def _escribir_archivo(self):
        nombre = self.nombre_archivo_entry.get()
        contenido = self.contenido_archivo_entry.get()
        if self.sistema_archivos.escribir_archivo(nombre, contenido):
            messagebox.showinfo("Archivo Actualizado", f"Contenido de '{nombre}' actualizado")
        else:
            messagebox.showerror("Error", f"El archivo '{nombre}' no existe")


# Ejecución principal
if __name__ == "__main__":
    sistema_operativo = SistemaOperativoSimulador()
    sistema_operativo.crear_interfaz()
    sistema_operativo.root.mainloop()