# 📄 PDF Tool - Herramienta PDF

Aplicación de escritorio para manipular archivos PDF con interfaz gráfica moderna.

## ✨ Funcionalidades

- **✂ Dividir PDF**: Divide un PDF por rangos de páginas, cada N páginas, o extrae todas las páginas individuales.
- **📎 Unir PDFs**: Combina múltiples archivos PDF en uno solo, con opción de reordenar.
- **📝 Convertir a Word**: Convierte archivos PDF a formato Word (.docx) manteniendo el formato.

## 📋 Requisitos

- Python 3.14 o superior
- pip (gestor de paquetes de Python)

## 🚀 Instalación

1. Clonar o descargar este repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd PDFs
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Uso

Ejecutar la aplicación:
```bash
python main.py
```

Se abrirá una ventana con tres pestañas:

### ✂ Dividir
1. Selecciona el archivo PDF de entrada
2. Elige el modo de división:
   - **Por rango**: Especifica rangos como `1-3, 5, 7-10`
   - **Cada N páginas**: Divide el PDF en bloques de N páginas
   - **Todas las páginas**: Extrae cada página como archivo individual
3. Selecciona la carpeta de salida
4. Haz clic en "Dividir PDF"

### 📎 Unir
1. Agrega los archivos PDF que deseas unir
2. Usa los botones ⬆⬇ para reordenar
3. Selecciona el archivo de salida
4. Haz clic en "Unir PDFs"

### 📝 Convertir
1. Agrega los archivos PDF a convertir
2. Selecciona la carpeta de salida
3. Haz clic en "Convertir a Word"

## 🛠 Tecnologías

| Librería | Uso |
|---|---|
| [pypdf](https://github.com/py-pdf/pypdf) | Manipulación de PDFs (dividir, unir) |
| [pdf2docx](https://github.com/ArtifexSoftware/pdf2docx) | Conversión de PDF a Word |
| [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) | Interfaz gráfica moderna |

## 📁 Estructura del Proyecto

```
PDFs/
├── main.py              # Punto de entrada
├── requirements.txt     # Dependencias
├── README.md            # Este archivo
├── core/                # Lógica de procesamiento
│   ├── splitter.py      # División de PDFs
│   ├── merger.py        # Unión de PDFs
│   └── converter.py     # Conversión a Word
└── gui/                 # Interfaz gráfica
    ├── app.py           # Ventana principal
    ├── split_tab.py     # Pestaña Dividir
    ├── merge_tab.py     # Pestaña Unir
    └── convert_tab.py   # Pestaña Convertir
```

## 📄 Licencia

MIT
