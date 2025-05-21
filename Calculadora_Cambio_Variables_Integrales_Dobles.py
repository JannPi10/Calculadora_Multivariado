import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import cm
from mpl_toolkits.mplot3d import art3d
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from sympy import symbols, diff, Matrix, lambdify, latex, sqrt, log, exp, sin, cos, tan, pi, E

class CalculadoraAvanzada:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora Avanzada de Cambio de Variables en Integrales Dobles")
        self.root.geometry("1200x800")
        
        # Símbolos para cálculos simbólicos
        self.x, self.y, self.u, self.v, self.r, self.theta = symbols('x y u v r theta')
        
        # Lista de funciones
        self.funciones = []
        
        # Variable para almacenar el campo de entrada activo
        self.campo_activo = None
        
        # Crear pestañas principales
        self.tab_control = ttk.Notebook(root)
        
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab3 = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab1, text='Calculadora')
        self.tab_control.add(self.tab2, text='Gráficas')
        self.tab_control.add(self.tab3, text='Ayuda')
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Configurar la pestaña de calculadora
        self.setup_calculator_tab()
        
        # Configurar la pestaña de gráficas
        self.setup_graph_tab()
        
        # Configurar la pestaña de ayuda
        self.setup_help_tab()
        
        # Añadir la primera función por defecto
        self.agregar_funcion()
        
        # Configurar el seguimiento del campo activo
        self.configurar_seguimiento_campo_activo()
    
    def configurar_seguimiento_campo_activo(self):
        # Configurar el seguimiento del campo activo para todos los widgets
        def configurar_widget(widget):
            if isinstance(widget, (ttk.Entry, tk.Entry)):
                widget.bind("<FocusIn>", self.actualizar_campo_activo)
            
            # Recursivamente configurar todos los widgets hijos
            for child in widget.winfo_children():
                configurar_widget(child)
        
        # Iniciar la configuración desde el widget raíz
        configurar_widget(self.root)
    
    def actualizar_campo_activo(self, event):
        # Actualizar el campo activo cuando un widget recibe el foco
        self.campo_activo = event.widget
        
        # Actualizar la etiqueta que muestra el campo activo
        if self.campo_activo:
            # Intentar determinar qué campo es
            campo_nombre = "Campo desconocido"
            
            # Verificar si es un campo de función
            for i, func in enumerate(self.funciones):
                if self.campo_activo == func["entry"]:
                    campo_nombre = f"Función {i+1}"
                    break
            
            # Verificar otros campos comunes
            if self.campo_activo == getattr(self, 'x_min_entry', None):
                campo_nombre = "Límite mínimo de x"
            elif self.campo_activo == getattr(self, 'x_max_entry', None):
                campo_nombre = "Límite máximo de x"
            elif self.campo_activo == getattr(self, 'y_min_entry', None):
                campo_nombre = "Límite mínimo de y"
            elif self.campo_activo == getattr(self, 'y_max_entry', None):
                campo_nombre = "Límite máximo de y"
            elif self.campo_activo == getattr(self, 'x_transform_entry', None):
                campo_nombre = "Transformación x(u,v)"
            elif self.campo_activo == getattr(self, 'y_transform_entry', None):
                campo_nombre = "Transformación y(u,v)"
            elif self.campo_activo == getattr(self, 'u_min_entry', None):
                campo_nombre = "Límite mínimo de u"
            elif self.campo_activo == getattr(self, 'u_max_entry', None):
                campo_nombre = "Límite máximo de u"
            elif self.campo_activo == getattr(self, 'v_min_entry', None):
                campo_nombre = "Límite mínimo de v"
            elif self.campo_activo == getattr(self, 'v_max_entry', None):
                campo_nombre = "Límite máximo de v"
            elif self.campo_activo == getattr(self, 'r_min_entry', None):
                campo_nombre = "Límite mínimo de r"
            elif self.campo_activo == getattr(self, 'r_max_entry', None):
                campo_nombre = "Límite máximo de r"
            elif self.campo_activo == getattr(self, 'theta_min_entry', None):
                campo_nombre = "Límite mínimo de θ"
            elif self.campo_activo == getattr(self, 'theta_max_entry', None):
                campo_nombre = "Límite máximo de θ"
            elif self.campo_activo == getattr(self, 'center_x_entry', None):
                campo_nombre = "Centro x"
            elif self.campo_activo == getattr(self, 'center_y_entry', None):
                campo_nombre = "Centro y"
            elif self.campo_activo == getattr(self, 'radius_entry', None):
                campo_nombre = "Radio"
            elif self.campo_activo == getattr(self, 'region_constraint1', None):
                campo_nombre = "Restricción 1"
            elif self.campo_activo == getattr(self, 'region_constraint2', None):
                campo_nombre = "Restricción 2"
            elif self.campo_activo == getattr(self, 'param_a_entry', None):
                campo_nombre = "Parámetro a"
            elif self.campo_activo == getattr(self, 'param_b_entry', None):
                campo_nombre = "Parámetro b"
            
            self.campo_activo_var.set(campo_nombre)
        else:
            self.campo_activo_var.set("Ninguno")
    
    def setup_calculator_tab(self):
        # Frame principal con scroll
        main_frame = ttk.Frame(self.tab1)
        main_frame.pack(fill="both", expand=True)
        
        # Canvas con scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Barra de símbolos matemáticos (ahora en la parte superior)
        symbols_frame = ttk.LabelFrame(scrollable_frame, text="Símbolos Matemáticos")
        symbols_frame.pack(fill="x", padx=10, pady=10)
        
        # Selector de campo activo
        selector_frame = ttk.Frame(symbols_frame)
        selector_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(selector_frame, text="Campo activo:").pack(side="left", padx=5)
        self.campo_activo_var = tk.StringVar(value="Ninguno")
        self.campo_activo_label = ttk.Label(selector_frame, textvariable=self.campo_activo_var)
        self.campo_activo_label.pack(side="left", padx=5)
        
        # Botones de símbolos
        buttons_frame = ttk.Frame(symbols_frame)
        buttons_frame.pack(fill="x", padx=5, pady=5)
        
        symbols = [
            ("π", "pi"), ("e", "E"), ("√", "sqrt()"), 
            ("log", "log()"), ("ln", "log()"), ("exp", "exp()"),
            ("sin", "sin()"), ("cos", "cos()"), ("tan", "tan()"),
            ("^", "**"), ("∫", "integral")
        ]
        
        for i, (symbol, code) in enumerate(symbols):
            ttk.Button(buttons_frame, text=symbol, width=5,
                      command=lambda c=code: self.insertar_simbolo(c)).grid(row=i//6, column=i%6, padx=2, pady=2)
        
        # Frame para funciones
        self.funciones_frame = ttk.LabelFrame(scrollable_frame, text="Funciones")
        self.funciones_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Botones para agregar/eliminar funciones
        func_buttons_frame = ttk.Frame(self.funciones_frame)
        func_buttons_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(func_buttons_frame, text="Agregar Función", command=self.agregar_funcion).pack(side="left", padx=5)
        ttk.Button(func_buttons_frame, text="Eliminar Función", command=self.eliminar_funcion).pack(side="left", padx=5)
        
        # Frame para la lista de funciones
        self.lista_funciones_frame = ttk.Frame(self.funciones_frame)
        self.lista_funciones_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Frame para región de integración
        region_frame = ttk.LabelFrame(scrollable_frame, text="Región de Integración")
        region_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tipo de región
        ttk.Label(region_frame, text="Tipo de Región:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.region_type = tk.StringVar(value="rectangular")
        region_combo = ttk.Combobox(region_frame, textvariable=self.region_type, 
                                   values=["rectangular", "circular", "personalizada"])
        region_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        region_combo.bind("<<ComboboxSelected>>", self.actualizar_region)
        
        # Frame para parámetros de región
        self.region_params_frame = ttk.Frame(region_frame)
        self.region_params_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # Inicializar con región rectangular
        self.setup_rectangular_region()
        
        # Frame para transformación
        transform_frame = ttk.LabelFrame(scrollable_frame, text="Transformación")
        transform_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tipo de transformación
        ttk.Label(transform_frame, text="Tipo de Transformación:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.transform_type = tk.StringVar(value="personalizada")
        transform_combo = ttk.Combobox(transform_frame, textvariable=self.transform_type, 
                                      values=["polar", "elíptica", "hiperbólica", "personalizada"])
        transform_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        transform_combo.bind("<<ComboboxSelected>>", self.actualizar_transformacion)
        
        # Frame para parámetros de transformación
        self.transform_params_frame = ttk.Frame(transform_frame)
        self.transform_params_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # Inicializar con transformación personalizada
        self.setup_custom_transform()
        
        # Botones de acción
        action_frame = ttk.Frame(scrollable_frame)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(action_frame, text="Calcular", command=self.calcular).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Graficar", command=self.graficar).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Limpiar", command=self.limpiar).pack(side="left", padx=5)
        
        # Frame para resultados
        result_frame = ttk.LabelFrame(scrollable_frame, text="Resultados")
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Área de texto para resultados
        self.result_text = scrolledtext.ScrolledText(result_frame, width=80, height=15, wrap=tk.WORD)
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def setup_graph_tab(self):
        # Frame para controles de gráfica
        controls_frame = ttk.Frame(self.tab2)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(controls_frame, text="Tipo de Gráfica:").pack(side="left", padx=5)
        self.graph_type = tk.StringVar(value="region")
        graph_combo = ttk.Combobox(controls_frame, textvariable=self.graph_type, 
                                  values=["region", "funcion", "transformacion"])
        graph_combo.pack(side="left", padx=5)
        
        ttk.Button(controls_frame, text="Actualizar Gráfica", 
                  command=lambda: self.actualizar_grafica()).pack(side="left", padx=5)
        
        # Frame para la gráfica
        self.graph_frame = ttk.Frame(self.tab2)
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear figura inicial
        self.fig = Figure(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def setup_help_tab(self):
        help_text = """
        # Calculadora Avanzada de Cambio de Variables en Integrales Dobles
        
        Esta calculadora te permite realizar cambios de variables en integrales dobles con múltiples funciones y regiones.
        
        ## Cómo usar:
        
        1. **Funciones**:
           - Puedes agregar múltiples funciones f(x,y)
           - Usa la sintaxis de Python: x**2 (no x^2), sqrt(x), etc.
           - Puedes usar los botones de símbolos matemáticos para insertar expresiones comunes
        
        2. **Región de Integración**:
           - Rectangular: Define límites para x e y
           - Circular: Define centro y radio
           - Personalizada: Define la región mediante desigualdades
        
        3. **Transformación**:
           - Polar: x = r·cos(θ), y = r·sin(θ)
           - Elíptica: x = a·r·cos(θ), y = b·r·sin(θ)
           - Hiperbólica: x = u·v, y = (u²-v²)/2
           - Personalizada: Define tus propias ecuaciones
        
        4. **Cálculo**:
           - Calcula el jacobiano y la integral transformada
           - Visualiza las regiones y funciones
        
        ## Símbolos y Funciones Disponibles:
        
        - Constantes: π (pi), e (E)
        - Funciones trigonométricas: sin(x), cos(x), tan(x)
        - Funciones exponenciales y logarítmicas: exp(x), log(x)
        - Raíz cuadrada: sqrt(x)
        - Potencias: x**y
        
        ## Ejemplos:
        
        ### Ejemplo 1: Área de un círculo
        - Función: 1
        - Región: Circular con centro (0,0) y radio 1
        - Transformación: Polar
        
        ### Ejemplo 2: Volumen bajo z = x² + y²
        - Función: x**2 + y**2
        - Región: Rectangular con x,y ∈ [0,1]
        - Transformación: Personalizada
        
        ## Uso de la Barra de Símbolos:
        
        1. Haz clic en el campo donde quieres insertar un símbolo
        2. Verás que el "Campo activo" se actualiza
        3. Haz clic en el símbolo que deseas insertar
        4. El símbolo se insertará en la posición del cursor
        """
        
        help_display = scrolledtext.ScrolledText(self.tab3, wrap=tk.WORD)
        help_display.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        help_display.insert(tk.END, help_text)
        help_display.config(state=tk.DISABLED)
    
    def agregar_funcion(self):
        # Crear un nuevo frame para la función
        func_id = len(self.funciones)
        func_frame = ttk.LabelFrame(self.lista_funciones_frame, text=f"Función {func_id + 1}")
        func_frame.pack(fill="x", padx=5, pady=5)
        
        # Entrada para la función
        ttk.Label(func_frame, text="f(x,y) =").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        func_entry = ttk.Entry(func_frame, width=50)
        func_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        func_entry.insert(0, "x**2 + y**2" if func_id == 0 else "")
        
        # Configurar el seguimiento del campo activo
        func_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        # Guardar referencia a los widgets
        self.funciones.append({
            "frame": func_frame,
            "entry": func_entry
        })
    
    def eliminar_funcion(self):
        if len(self.funciones) > 1:
            # Eliminar la última función
            func = self.funciones.pop()
            func["frame"].destroy()
        else:
            messagebox.showinfo("Información", "Debe haber al menos una función")
    
    def setup_rectangular_region(self):
        # Limpiar frame
        for widget in self.region_params_frame.winfo_children():
            widget.destroy()
        
        # Límites de x
        ttk.Label(self.region_params_frame, text="Límites de x:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.x_min_entry = ttk.Entry(self.region_params_frame, width=10)
        self.x_min_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.x_min_entry.insert(0, "0")
        self.x_min_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        ttk.Label(self.region_params_frame, text="≤ x ≤").grid(row=0, column=2, padx=5, pady=5)
        
        self.x_max_entry = ttk.Entry(self.region_params_frame, width=10)
        self.x_max_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.x_max_entry.insert(0, "1")
        self.x_max_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        # Límites de y
        ttk.Label(self.region_params_frame, text="Límites de y:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.y_min_entry = ttk.Entry(self.region_params_frame, width=10)
        self.y_min_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.y_min_entry.insert(0, "0")
        self.y_min_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        ttk.Label(self.region_params_frame, text="≤ y ≤").grid(row=1, column=2, padx=5, pady=5)
        
        self.y_max_entry = ttk.Entry(self.region_params_frame, width=10)
        self.y_max_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.y_max_entry.insert(0, "1")
        self.y_max_entry.bind("<FocusIn>", self.actualizar_campo_activo)
    
    def setup_circular_region(self):
        # Limpiar frame
        for widget in self.region_params_frame.winfo_children():
            widget.destroy()
        
        # Centro del círculo
        ttk.Label(self.region_params_frame, text="Centro (x₀, y₀):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.center_x_entry = ttk.Entry(self.region_params_frame, width=10)
        self.center_x_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.center_x_entry.insert(0, "0")
        self.center_x_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        self.center_y_entry = ttk.Entry(self.region_params_frame, width=10)
        self.center_y_entry.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.center_y_entry.insert(0, "0")
        self.center_y_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        # Radio
        ttk.Label(self.region_params_frame, text="Radio:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.radius_entry = ttk.Entry(self.region_params_frame, width=10)
        self.radius_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.radius_entry.insert(0, "1")
        self.radius_entry.bind("<FocusIn>", self.actualizar_campo_activo)
    
    def setup_custom_region(self):
        # Limpiar frame
        for widget in self.region_params_frame.winfo_children():
            widget.destroy()
        
        # Descripción
        ttk.Label(self.region_params_frame, 
                 text="Define la región mediante desigualdades o ecuaciones:").grid(
                     row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Restricción 1
        ttk.Label(self.region_params_frame, text="Restricción 1:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.region_constraint1 = ttk.Entry(self.region_params_frame, width=50)
        self.region_constraint1.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.region_constraint1.insert(0, "x**2 + y**2 <= 1")
        self.region_constraint1.bind("<FocusIn>", self.actualizar_campo_activo)
        
        # Restricción 2
        ttk.Label(self.region_params_frame, text="Restricción 2:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.region_constraint2 = ttk.Entry(self.region_params_frame, width=50)
        self.region_constraint2.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.region_constraint2.insert(0, "x >= 0 and y >= 0")
        self.region_constraint2.bind("<FocusIn>", self.actualizar_campo_activo)
        
        # Nota
        ttk.Label(self.region_params_frame, 
                 text="Nota: Usa operadores de comparación (<=, >=, ==) y lógicos (and, or)").grid(
                     row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")
    
    def setup_polar_transform(self):
        # Limpiar frame
        for widget in self.transform_params_frame.winfo_children():
            widget.destroy()
        
        # Mostrar las ecuaciones
        ttk.Label(self.transform_params_frame, text="x = r·cos(θ)").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(self.transform_params_frame, text="y = r·sin(θ)").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        # Límites de r
        ttk.Label(self.transform_params_frame, text="Límites de r:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.r_min_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.r_min_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.r_min_entry.insert(0, "0")
        self.r_min_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        ttk.Label(self.transform_params_frame, text="≤ r ≤").grid(row=2, column=2, padx=5, pady=5)
        
        self.r_max_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.r_max_entry.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        self.r_max_entry.insert(0, "1")
        self.r_max_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        # Límites de theta
        ttk.Label(self.transform_params_frame, text="Límites de θ:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.theta_min_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.theta_min_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.theta_min_entry.insert(0, "0")
        self.theta_min_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        ttk.Label(self.transform_params_frame, text="≤ θ ≤").grid(row=3, column=2, padx=5, pady=5)
        
        self.theta_max_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.theta_max_entry.grid(row=3, column=3, padx=5, pady=5, sticky="w")
        self.theta_max_entry.insert(0, "2*pi")
        self.theta_max_entry.bind("<FocusIn>", self.actualizar_campo_activo)
    
    def setup_elliptic_transform(self):
        # Limpiar frame
        for widget in self.transform_params_frame.winfo_children():
            widget.destroy()
        
        # Parámetros a y b
        ttk.Label(self.transform_params_frame, text="Parámetro a:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.param_a_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.param_a_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.param_a_entry.insert(0, "2")
        self.param_a_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        ttk.Label(self.transform_params_frame, text="Parámetro b:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.param_b_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.param_b_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.param_b_entry.insert(0, "1")
        self.param_b_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        # Mostrar las ecuaciones
        ttk.Label(self.transform_params_frame, text="x = a·r·cos(θ)").grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        ttk.Label(self.transform_params_frame, text="y = b·r·sin(θ)").grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Límites de r
        ttk.Label(self.transform_params_frame, text="Límites de r:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.r_min_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.r_min_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.r_min_entry.insert(0, "0")
        self.r_min_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        ttk.Label(self.transform_params_frame, text="≤ r ≤").grid(row=4, column=2, padx=5, pady=5)
        
        self.r_max_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.r_max_entry.grid(row=4, column=3, padx=5, pady=5, sticky="w")
        self.r_max_entry.insert(0, "1")
        self.r_max_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        # Límites de theta
        ttk.Label(self.transform_params_frame, text="Límites de θ:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.theta_min_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.theta_min_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.theta_min_entry.insert(0, "0")
        self.theta_min_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        ttk.Label(self.transform_params_frame, text="≤ θ ≤").grid(row=5, column=2, padx=5, pady=5)
        
        self.theta_max_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.theta_max_entry.grid(row=5, column=3, padx=5, pady=5, sticky="w")
        self.theta_max_entry.insert(0, "2*pi")
        self.theta_max_entry.bind("<FocusIn>", self.actualizar_campo_activo)
    
    def setup_hyperbolic_transform(self):
        # Limpiar frame
        for widget in self.transform_params_frame.winfo_children():
            widget.destroy()
        
        # Mostrar las ecuaciones
        ttk.Label(self.transform_params_frame, text="x = u·v").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(self.transform_params_frame, text="y = (u²-v²)/2").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        # Límites de u
        ttk.Label(self.transform_params_frame, text="Límites de u:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.u_min_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.u_min_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.u_min_entry.insert(0, "0")
        self.u_min_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        ttk.Label(self.transform_params_frame, text="≤ u ≤").grid(row=2, column=2, padx=5, pady=5)
        
        self.u_max_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.u_max_entry.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        self.u_max_entry.insert(0, "1")
        self.u_max_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        # Límites de v
        ttk.Label(self.transform_params_frame, text="Límites de v:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.v_min_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.v_min_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.v_min_entry.insert(0, "0")
        self.v_min_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        ttk.Label(self.transform_params_frame, text="≤ v ≤").grid(row=3, column=2, padx=5, pady=5)
        
        self.v_max_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.v_max_entry.grid(row=3, column=3, padx=5, pady=5, sticky="w")
        self.v_max_entry.insert(0, "1")
        self.v_max_entry.bind("<FocusIn>", self.actualizar_campo_activo)
    
    def setup_custom_transform(self):
        # Limpiar frame
        for widget in self.transform_params_frame.winfo_children():
            widget.destroy()
        
        # Transformación x
        ttk.Label(self.transform_params_frame, text="x = x(u,v):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.x_transform_entry = ttk.Entry(self.transform_params_frame, width=50)
        self.x_transform_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.x_transform_entry.insert(0, "u*cos(v)")
        self.x_transform_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        # Transformación y
        ttk.Label(self.transform_params_frame, text="y = y(u,v):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.y_transform_entry = ttk.Entry(self.transform_params_frame, width=50)
        self.y_transform_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.y_transform_entry.insert(0, "u*sin(v)")
        self.y_transform_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        # Límites de u
        ttk.Label(self.transform_params_frame, text="Límites de u:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.u_min_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.u_min_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.u_min_entry.insert(0, "0")
        self.u_min_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        ttk.Label(self.transform_params_frame, text="≤ u ≤").grid(row=2, column=2, padx=5, pady=5)
        
        self.u_max_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.u_max_entry.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        self.u_max_entry.insert(0, "1")
        self.u_max_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        # Límites de v
        ttk.Label(self.transform_params_frame, text="Límites de v:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.v_min_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.v_min_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.v_min_entry.insert(0, "0")
        self.v_min_entry.bind("<FocusIn>", self.actualizar_campo_activo)
        
        ttk.Label(self.transform_params_frame, text="≤ v ≤").grid(row=3, column=2, padx=5, pady=5)
        
        self.v_max_entry = ttk.Entry(self.transform_params_frame, width=10)
        self.v_max_entry.grid(row=3, column=3, padx=5, pady=5, sticky="w")
        self.v_max_entry.insert(0, "2*pi")
        self.v_max_entry.bind("<FocusIn>", self.actualizar_campo_activo)
    
    def actualizar_region(self, event=None):
        region_type = self.region_type.get()
        
        if region_type == "rectangular":
            self.setup_rectangular_region()
        elif region_type == "circular":
            self.setup_circular_region()
        elif region_type == "personalizada":
            self.setup_custom_region()
    
    def actualizar_transformacion(self, event=None):
        transform_type = self.transform_type.get()
        
        if transform_type == "polar":
            self.setup_polar_transform()
        elif transform_type == "elíptica":
            self.setup_elliptic_transform()
        elif transform_type == "hiperbólica":
            self.setup_hyperbolic_transform()
        elif transform_type == "personalizada":
            self.setup_custom_transform()
    
    def insertar_simbolo(self, symbol):
        # Verificar si hay un campo activo
        if not self.campo_activo:
            messagebox.showinfo("Información", "Primero haz clic en un campo para seleccionarlo")
            return
        
        # Verificar si es un widget de entrada
        if isinstance(self.campo_activo, (ttk.Entry, tk.Entry)):
            # Obtener la posición del cursor
            pos = self.campo_activo.index(tk.INSERT)
            
            # Insertar el símbolo en la posición del cursor
            if symbol == "integral":
                messagebox.showinfo("Información", "La integral se calcula automáticamente")
                return
            
            self.campo_activo.insert(pos, symbol)
            
            # Si el símbolo tiene paréntesis, colocar el cursor dentro
            if "(" in symbol and ")" in symbol:
                # Colocar el cursor entre los paréntesis
                self.campo_activo.icursor(pos + symbol.index("(") + 1)
        else:
            messagebox.showinfo("Información", "El campo seleccionado no permite insertar símbolos")
    
    def obtener_transformacion(self):
        transform_type = self.transform_type.get()
    
        try:
            if transform_type == "polar":
                # Definir las expresiones simbólicas para la transformación polar
                x_transform = self.r * sp.cos(self.theta)
                y_transform = self.r * sp.sin(self.theta)
                
                # Obtener los límites numéricos
                r_min_expr = parse_expr(self.r_min_entry.get())
                r_max_expr = parse_expr(self.r_max_entry.get())
                theta_min_expr = parse_expr(self.theta_min_entry.get())
                theta_max_expr = parse_expr(self.theta_max_entry.get())
                
                u_min = float(r_min_expr.evalf())
                u_max = float(r_max_expr.evalf())
                v_min = float(theta_min_expr.evalf())
                v_max = float(theta_max_expr.evalf())
                
                return x_transform, y_transform, u_min, u_max, v_min, v_max
                
            elif transform_type == "elíptica":
                # Obtener los parámetros a y b
                a_expr = parse_expr(self.param_a_entry.get())
                b_expr = parse_expr(self.param_b_entry.get())
                
                # Convertir a valores numéricos si es posible
                try:
                    a = float(a_expr.evalf())
                    b = float(b_expr.evalf())
                except:
                    # Si no se pueden convertir, usar los símbolos
                    a = a_expr
                    b = b_expr
                
                # Definir las expresiones simbólicas para la transformación elíptica
                x_transform = a * self.r * sp.cos(self.theta)
                y_transform = b * self.r * sp.sin(self.theta)
                
                # Obtener los límites numéricos
                r_min_expr = parse_expr(self.r_min_entry.get())
                r_max_expr = parse_expr(self.r_max_entry.get())
                theta_min_expr = parse_expr(self.theta_min_entry.get())
                theta_max_expr = parse_expr(self.theta_max_entry.get())
                
                u_min = float(r_min_expr.evalf())
                u_max = float(r_max_expr.evalf())
                v_min = float(theta_min_expr.evalf())
                v_max = float(theta_max_expr.evalf())
                
                return x_transform, y_transform, u_min, u_max, v_min, v_max
                
            elif transform_type == "hiperbólica":
                # Definir las expresiones simbólicas para la transformación hiperbólica
                x_transform = self.u * self.v
                y_transform = (self.u**2 - self.v**2) / 2
                
                # Obtener los límites numéricos
                u_min_expr = parse_expr(self.u_min_entry.get())
                u_max_expr = parse_expr(self.u_max_entry.get())
                v_min_expr = parse_expr(self.v_min_entry.get())
                v_max_expr = parse_expr(self.v_max_entry.get())
                
                u_min = float(u_min_expr.evalf())
                u_max = float(u_max_expr.evalf())
                v_min = float(v_min_expr.evalf())
                v_max = float(v_max_expr.evalf())
                
                return x_transform, y_transform, u_min, u_max, v_min, v_max
                
            elif transform_type == "personalizada":
                # Parsear expresiones con transformaciones estándar
                transformations = standard_transformations + (implicit_multiplication_application,)
                
                # Obtener las expresiones de transformación
                x_transform_str = self.x_transform_entry.get()
                y_transform_str = self.y_transform_entry.get()
                
                # Parsear las expresiones
                x_transform = parse_expr(x_transform_str, transformations=transformations)
                y_transform = parse_expr(y_transform_str, transformations=transformations)
                
                # Obtener los límites numéricos
                u_min_expr = parse_expr(self.u_min_entry.get())
                u_max_expr = parse_expr(self.u_max_entry.get())
                v_min_expr = parse_expr(self.v_min_entry.get())
                v_max_expr = parse_expr(self.v_max_entry.get())
                
                u_min = float(u_min_expr.evalf())
                u_max = float(u_max_expr.evalf())
                v_min = float(v_min_expr.evalf())
                v_max = float(v_max_expr.evalf())
                
                return x_transform, y_transform, u_min, u_max, v_min, v_max
    
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener la transformación: {str(e)}")
            # Devolver una transformación por defecto en caso de error
            return self.u, self.v, 0, 1, 0, 1
    
    def obtener_region(self):
        region_type = self.region_type.get()
        
        if region_type == "rectangular":
            x_min = float(parse_expr(self.x_min_entry.get()).evalf())
            x_max = float(parse_expr(self.x_max_entry.get()).evalf())
            y_min = float(parse_expr(self.y_min_entry.get()).evalf())
            y_max = float(parse_expr(self.y_max_entry.get()).evalf())
            
            return "rectangular", (x_min, x_max, y_min, y_max)
            
        elif region_type == "circular":
            center_x = float(parse_expr(self.center_x_entry.get()).evalf())
            center_y = float(parse_expr(self.center_y_entry.get()).evalf())
            radius = float(parse_expr(self.radius_entry.get()).evalf())
            
            return "circular", (center_x, center_y, radius)
            
        elif region_type == "personalizada":
            constraint1 = self.region_constraint1.get()
            constraint2 = self.region_constraint2.get()
            
            return "personalizada", (constraint1, constraint2)
    
    def calcular(self):
        try:
            # Limpiar resultados
            self.result_text.delete(1.0, tk.END)
            
            # Obtener funciones
            funciones = []
            for func in self.funciones:
                func_str = func["entry"].get()
                if func_str.strip():
                    # Parsear expresión con transformaciones estándar
                    transformations = standard_transformations + (implicit_multiplication_application,)
                    funciones.append(parse_expr(func_str, transformations=transformations))
            
            if not funciones:
                messagebox.showwarning("Advertencia", "Debe ingresar al menos una función")
                return
            
            # Obtener transformación
            x_transform, y_transform, u_min, u_max, v_min, v_max = self.obtener_transformacion()
            
            # Determinar las variables para el cálculo del jacobiano según el tipo de transformación
            transform_type = self.transform_type.get()
            if transform_type == "polar" or transform_type == "elíptica":
                var1, var2 = self.r, self.theta
            else:  # "hiperbólica" o "personalizada"
                var1, var2 = self.u, self.v
            
            # Calcular el jacobiano con las variables correctas
            dx_du = diff(x_transform, var1)
            dx_dv = diff(x_transform, var2)
            dy_du = diff(y_transform, var1)
            dy_dv = diff(y_transform, var2)
            
            jacobian_matrix = Matrix([[dx_du, dx_dv], [dy_du, dy_dv]])
            jacobian_det = jacobian_matrix.det()
            
            # Simplificar el determinante jacobiano
            jacobian_det_simplified = sp.simplify(jacobian_det)
            
            # Mostrar resultados
            self.result_text.insert(tk.END, "=== RESULTADOS DEL CAMBIO DE VARIABLES ===\n\n")
            
            # Mostrar funciones originales
            self.result_text.insert(tk.END, "Funciones originales:\n")
            for i, func in enumerate(funciones):
                self.result_text.insert(tk.END, f"f{i+1}(x,y) = {func}\n")
            self.result_text.insert(tk.END, "\n")
            
            # Mostrar transformación
            self.result_text.insert(tk.END, "Transformación:\n")
            self.result_text.insert(tk.END, f"x = {x_transform}\n")
            self.result_text.insert(tk.END, f"y = {y_transform}\n\n")
            
            # Mostrar variables utilizadas para el jacobiano
            if transform_type == "polar":
                var_names = "r, θ"
            elif transform_type == "elíptica":
                var_names = "r, θ"
            elif transform_type == "hiperbólica":
                var_names = "u, v"
            else:
                var_names = "u, v"
            
            self.result_text.insert(tk.END, f"Variables para el jacobiano: {var_names}\n\n")
            
            # Mostrar matriz jacobiana
            self.result_text.insert(tk.END, "Matriz Jacobiana:\n")
            
            # Simplificar cada elemento de la matriz jacobiana
            simplified_matrix = Matrix([
                [sp.simplify(dx_du), sp.simplify(dx_dv)],
                [sp.simplify(dy_du), sp.simplify(dy_dv)]
            ])
            
            self.result_text.insert(tk.END, f"J = \n{simplified_matrix}\n\n")
            
            # Mostrar determinante jacobiano
            self.result_text.insert(tk.END, "Determinante Jacobiano:\n")
            self.result_text.insert(tk.END, f"|J| = {jacobian_det_simplified}\n\n")
            
            # Mostrar funciones transformadas
            self.result_text.insert(tk.END, "Funciones transformadas:\n")
            for i, func in enumerate(funciones):
                func_transformada = func.subs({self.x: x_transform, self.y: y_transform})
                # Simplificar la función transformada
                func_transformada_simplified = sp.simplify(func_transformada)
                
                if transform_type == "polar" or transform_type == "elíptica":
                    self.result_text.insert(tk.END, f"f{i+1}(r,θ) = {func_transformada_simplified}\n")
                else:
                    self.result_text.insert(tk.END, f"f{i+1}(u,v) = {func_transformada_simplified}\n")
            self.result_text.insert(tk.END, "\n")
            
            # Mostrar integrales transformadas
            self.result_text.insert(tk.END, "Integrales transformadas:\n")
            for i, func in enumerate(funciones):
                func_transformada = func.subs({self.x: x_transform, self.y: y_transform})
                integral_transformada = func_transformada * abs(jacobian_det)
                
                # Simplificar la integral transformada
                integral_transformada_simplified = sp.simplify(integral_transformada)
                
                # Ajustar la notación de las variables según el tipo de transformación
                if transform_type == "polar" or transform_type == "elíptica":
                    self.result_text.insert(tk.END, f"∫∫ f{i+1}(x,y) dx dy = ∫∫ {integral_transformada_simplified} dr dθ\n")
                    # Mostrar en formato LaTeX
                    self.result_text.insert(tk.END, f"LaTeX: \\iint f_{i+1}(x,y) dx dy = \\iint {latex(integral_transformada_simplified)} dr d\\theta\n\n")
                else:
                    self.result_text.insert(tk.END, f"∫∫ f{i+1}(x,y) dx dy = ∫∫ {integral_transformada_simplified} du dv\n")
                    # Mostrar en formato LaTeX
                    self.result_text.insert(tk.END, f"LaTeX: \\iint f_{i+1}(x,y) dx dy = \\iint {latex(integral_transformada_simplified)} du dv\n\n")
            
            # Mostrar límites de integración con la notación correcta
            self.result_text.insert(tk.END, "Límites de integración transformados:\n")
            if transform_type == "polar" or transform_type == "elíptica":
                self.result_text.insert(tk.END, f"{u_min} ≤ r ≤ {u_max}\n")
                self.result_text.insert(tk.END, f"{v_min} ≤ θ ≤ {v_max}\n")
            else:
                self.result_text.insert(tk.END, f"{u_min} ≤ u ≤ {u_max}\n")
                self.result_text.insert(tk.END, f"{v_min} ≤ v ≤ {v_max}\n")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error en el cálculo: {str(e)}")
    
    def graficar(self):
        try:
            # Actualizar la gráfica en la pestaña de gráficas
            self.actualizar_grafica()
            
            # Cambiar a la pestaña de gráficas
            self.tab_control.select(self.tab2)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la gráfica: {str(e)}")
    
    def actualizar_grafica(self):
        try:
            # Limpiar figura
            self.fig.clear()
            
            # Obtener tipo de gráfica
            graph_type = self.graph_type.get()
            
            if graph_type == "region":
                self.graficar_region()
            elif graph_type == "funcion":
                self.graficar_funcion()
            elif graph_type == "transformacion":
                self.graficar_transformacion()
            
            # Actualizar canvas
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar la gráfica: {str(e)}")
    
    def graficar_region(self):
        # Crear subplots
        ax1 = self.fig.add_subplot(121)
        ax2 = self.fig.add_subplot(122)
        
        # Obtener región
        region_type, region_params = self.obtener_region()
        
        # Graficar región original
        if region_type == "rectangular":
            x_min, x_max, y_min, y_max = region_params
            
            ax1.add_patch(plt.Rectangle((x_min, y_min), x_max-x_min, y_max-y_min, 
                                      fill=False, edgecolor='blue', linewidth=2))
            
            ax1.set_xlim(x_min - 0.5, x_max + 0.5)
            ax1.set_ylim(y_min - 0.5, y_max + 0.5)
            
        elif region_type == "circular":
            center_x, center_y, radius = region_params
            
            circle = plt.Circle((center_x, center_y), radius, fill=False, edgecolor='blue', linewidth=2)
            ax1.add_patch(circle)
            
            ax1.set_xlim(center_x - radius - 0.5, center_x + radius + 0.5)
            ax1.set_ylim(center_y - radius - 0.5, center_y + radius + 0.5)
            
        elif region_type == "personalizada":
            # Para regiones personalizadas, crear una malla y evaluar las restricciones
            constraint1, constraint2 = region_params
            
            # Crear una malla
            x = np.linspace(-3, 3, 100)
            y = np.linspace(-3, 3, 100)
            X, Y = np.meshgrid(x, y)
            
            # Evaluar restricciones
            mask = np.zeros_like(X, dtype=bool)
            
            # Reemplazar operadores de comparación por funciones
            constraint1 = constraint1.replace("<=", "<").replace(">=", ">")
            constraint2 = constraint2.replace("<=", "<").replace(">=", ">")
            
            # Crear funciones lambda para evaluar
            try:
                # Crear un entorno seguro
                safe_dict = {
                    'x': X, 'y': Y, 
                    'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                    'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
                    'pi': np.pi, 'e': np.e,
                    'and': np.logical_and, 'or': np.logical_or
                }
                
                # Evaluar restricciones
                if constraint1.strip():
                    mask1 = eval(constraint1, {"__builtins__": {}}, safe_dict)
                    mask = mask1
                
                if constraint2.strip():
                    mask2 = eval(constraint2, {"__builtins__": {}}, safe_dict)
                    mask = np.logical_and(mask, mask2)
                
                # Graficar región
                ax1.contourf(X, Y, mask, levels=[0.5, 1.5], colors=['blue'], alpha=0.3)
                ax1.contour(X, Y, mask, levels=[0.5], colors=['blue'], linewidths=2)
                
                # Ajustar límites
                ax1.set_xlim(-3, 3)
                ax1.set_ylim(-3, 3)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al evaluar restricciones: {str(e)}")
        
        # Configurar ejes
        ax1.set_xlabel('x')
        ax1.set_ylabel('y')
        ax1.set_title('Región Original (x,y)')
        ax1.grid(True)
        
        try:
            # Obtener transformación
            x_transform, y_transform, u_min, u_max, v_min, v_max = self.obtener_transformacion()
            
            # Crear malla para u y v
            u = np.linspace(u_min, u_max, 20)
            v = np.linspace(v_min, v_max, 20)
            U, V = np.meshgrid(u, v)
            
            # Determinar las variables para la transformación según el tipo
            transform_type = self.transform_type.get()
            if transform_type == "polar" or transform_type == "elíptica":
                var1, var2 = self.r, self.theta
            else:  # "hiperbólica" o "personalizada"
                var1, var2 = self.u, self.v
            
            # Crear funciones numéricas para la transformación usando lambdify
            x_func = lambdify((var1, var2), x_transform, modules="numpy")
            y_func = lambdify((var1, var2), y_transform, modules="numpy")
            
            # Aplicar las funciones de transformación a la malla
            try:
                if transform_type == "polar" or transform_type == "elíptica":
                    X_transformed = x_func(U, V)
                    Y_transformed = y_func(U, V)
                else:
                    X_transformed = x_func(U, V)
                    Y_transformed = y_func(U, V)
                
                # Dibujar la malla de la transformación
                for i in range(len(u)):
                    ax2.plot(X_transformed[:, i], Y_transformed[:, i], 'b-', alpha=0.5)
                for i in range(len(v)):
                    ax2.plot(X_transformed[i, :], Y_transformed[i, :], 'b-', alpha=0.5)
                
                # Ajustar límites para la región transformada
                x_transformed_min = np.min(X_transformed)
                x_transformed_max = np.max(X_transformed)
                y_transformed_min = np.min(Y_transformed)
                y_transformed_max = np.max(Y_transformed)
                
                padding = 0.5
                ax2.set_xlim(x_transformed_min - padding, x_transformed_max + padding)
                ax2.set_ylim(y_transformed_min - padding, y_transformed_max + padding)
                
                # Configurar ejes
                ax2.set_xlabel('x')
                ax2.set_ylabel('y')
                ax2.set_title('Espacio Transformado (x,y)')
                ax2.grid(True)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al aplicar la transformación: {str(e)}")
                # Mostrar un mensaje en el gráfico
                ax2.text(0.5, 0.5, "Error al aplicar la transformación", 
                        ha='center', va='center', transform=ax2.transAxes)
                ax2.set_xlabel('x')
                ax2.set_ylabel('y')
                ax2.set_title('Espacio Transformado (x,y)')
                ax2.grid(True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al graficar la región transformada: {str(e)}")
            # Mostrar un mensaje en el gráfico
            ax2.text(0.5, 0.5, "Error al graficar la región transformada", 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_xlabel('x')
            ax2.set_ylabel('y')
            ax2.set_title('Espacio Transformado (x,y)')
            ax2.grid(True)
    
    def graficar_transformacion(self):
        try:
            # Crear subplots
            ax1 = self.fig.add_subplot(121)
            ax2 = self.fig.add_subplot(122)
            
            # Obtener transformación
            x_transform, y_transform, u_min, u_max, v_min, v_max = self.obtener_transformacion()
            
            # Determinar las variables para la transformación según el tipo
            transform_type = self.transform_type.get()
            if transform_type == "polar" or transform_type == "elíptica":
                var1, var2 = self.r, self.theta
            else:  # "hiperbólica" o "personalizada"
                var1, var2 = self.u, self.v
            
            # Crear malla para u y v
            u = np.linspace(u_min, u_max, 20)
            v = np.linspace(v_min, v_max, 20)
            U, V = np.meshgrid(u, v)
            
            # Dibujar la malla en el espacio (u,v)
            for i in range(len(u)):
                ax1.plot(np.ones_like(v) * u[i], v, 'b-', alpha=0.5)
            for i in range(len(v)):
                ax1.plot(u, np.ones_like(u) * v[i], 'b-', alpha=0.5)
            
            # Configurar ejes
            ax1.set_xlabel('u' if transform_type == "hiperbólica" or transform_type == "personalizada" else 'r')
            ax1.set_ylabel('v' if transform_type == "hiperbólica" or transform_type == "personalizada" else 'θ')
            ax1.set_title('Espacio de Parámetros')
            ax1.grid(True)
            ax1.set_xlim(u_min - 0.5, u_max + 0.5)
            ax1.set_ylim(v_min - 0.5, v_max + 0.5)
            
            # Crear funciones numéricas para la transformación usando lambdify
            x_func = lambdify((var1, var2), x_transform, modules="numpy")
            y_func = lambdify((var1, var2), y_transform, modules="numpy")
            
            # Aplicar las funciones de transformación a la malla
            try:
                X_transformed = x_func(U, V)
                Y_transformed = y_func(U, V)
                
                # Dibujar la malla transformada
                for i in range(len(u)):
                    ax2.plot(X_transformed[:, i], Y_transformed[:, i], 'r-', alpha=0.5)
                for i in range(len(v)):
                    ax2.plot(X_transformed[i, :], Y_transformed[i, :], 'r-', alpha=0.5)
                
                # Ajustar límites para la región transformada
                x_transformed_min = np.min(X_transformed)
                x_transformed_max = np.max(X_transformed)
                y_transformed_min = np.min(Y_transformed)
                y_transformed_max = np.max(Y_transformed)
                
                padding = 0.5
                ax2.set_xlim(x_transformed_min - padding, x_transformed_max + padding)
                ax2.set_ylim(y_transformed_min - padding, y_transformed_max + padding)
                
                # Configurar ejes
                ax2.set_xlabel('x')
                ax2.set_ylabel('y')
                ax2.set_title('Espacio Transformado (x,y)')
                ax2.grid(True)
                
                # Añadir flechas para mostrar la dirección de la transformación
                self.fig.text(0.5, 0.95, 'Transformación: (u,v) → (x,y)', ha='center', va='center', fontsize=12)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al aplicar la transformación: {str(e)}")
                # Mostrar un mensaje en el gráfico
                ax2.text(0.5, 0.5, "Error al aplicar la transformación", 
                        ha='center', va='center', transform=ax2.transAxes)
                ax2.set_xlabel('x')
                ax2.set_ylabel('y')
                ax2.set_title('Espacio Transformado (x,y)')
                ax2.grid(True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al graficar la transformación: {str(e)}")
            # Mostrar un mensaje en el gráfico
            ax1.text(0.5, 0.5, "Error al graficar el espacio de parámetros", 
                    ha='center', va='center', transform=ax1.transAxes)
            ax2.text(0.5, 0.5, "Error al graficar la transformación", 
                    ha='center', va='center', transform=ax2.transAxes)
    
    def graficar_funcion(self):
        try:
            # Crear subplot 3D
            ax = self.fig.add_subplot(111, projection='3d')
            
            # Obtener la primera función
            if not self.funciones:
                messagebox.showwarning("Advertencia", "No hay funciones para graficar")
                return
            
            func_str = self.funciones[0]["entry"].get()
            if not func_str.strip():
                messagebox.showwarning("Advertencia", "La función está vacía")
                return
            
            # Parsear expresión
            transformations = standard_transformations + (implicit_multiplication_application,)
            func = parse_expr(func_str, transformations=transformations)
            
            # Obtener región
            region_type, region_params = self.obtener_region()
            
            # Definir dominio según la región
            if region_type == "rectangular":
                x_min, x_max, y_min, y_max = region_params
            elif region_type == "circular":
                center_x, center_y, radius = region_params
                x_min, x_max = center_x - radius, center_x + radius
                y_min, y_max = center_y - radius, center_y + radius
            else:
                # Para regiones personalizadas, usar un dominio predeterminado
                x_min, x_max, y_min, y_max = -2, 2, -2, 2
            
            # Crear malla
            x = np.linspace(x_min, x_max, 50)
            y = np.linspace(y_min, y_max, 50)
            X, Y = np.meshgrid(x, y)
            
            # Crear función numérica usando lambdify
            f_func = lambdify((self.x, self.y), func, modules="numpy")
            
            # Aplicar la función a la malla
            try:
                Z = f_func(X, Y)
                
                # Graficar superficie
                surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
                
                # Añadir barra de colores
                self.fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
                
                # Configurar ejes
                ax.set_xlabel('x')
                ax.set_ylabel('y')
                ax.set_zlabel('z')
                ax.set_title(f'Función: {func_str}')
                
                # Si es una región específica, marcarla
                if region_type == "rectangular":
                    # Crear los vértices del rectángulo
                    verts = [
                        [x_min, y_min, 0],
                        [x_max, y_min, 0],
                        [x_max, y_max, 0],
                        [x_min, y_max, 0]
                    ]
                    
                    # CORRECCIÓN: Crear la colección de polígonos correctamente
                    poly = art3d.Poly3DCollection([verts], alpha=0.3)
                    poly.set_color('red')
                    ax.add_collection3d(poly)
                    
                elif region_type == "circular":
                    # Crear puntos para el círculo
                    theta = np.linspace(0, 2*np.pi, 100)
                    x_circle = center_x + radius * np.cos(theta)
                    y_circle = center_y + radius * np.sin(theta)
                    z_circle = np.zeros_like(theta)
                    
                    # Graficar el círculo
                    ax.plot(x_circle, y_circle, z_circle, 'r-', linewidth=2)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al evaluar la función: {str(e)}")
                # Mostrar un mensaje en el gráfico
                ax.text2D(0.5, 0.5, "Error al evaluar la función", 
                        ha='center', va='center', transform=ax.transAxes)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al graficar la función: {str(e)}")
    
    def limpiar(self):
        # Limpiar funciones
        for func in self.funciones[1:]:
            func["frame"].destroy()
        
        self.funciones = [self.funciones[0]]
        self.funciones[0]["entry"].delete(0, tk.END)
        self.funciones[0]["entry"].insert(0, "x**2 + y**2")
        
        # Restablecer región a rectangular
        self.region_type.set("rectangular")
        self.actualizar_region()
        
        # Restablecer transformación a personalizada
        self.transform_type.set("personalizada")
        self.actualizar_transformacion()
        
        # Limpiar resultados
        self.result_text.delete(1.0, tk.END)
        
        # Limpiar gráficas
        self.fig.clear()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraAvanzada(root)
    root.mainloop()