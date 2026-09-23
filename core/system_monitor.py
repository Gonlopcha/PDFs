"""
system_monitor.py — Detección de RAM y procesamiento por lotes

Proporciona:
- Detección de RAM disponible vía API de Windows (ctypes, sin dependencias)
- Procesamiento por lotes (batch) para evitar congelamientos en máquinas con poca RAM al manejar Excel u otros procesos pesados.
- Integración con la GUI para mostrar advertencias y progreso
"""

import ctypes
import ctypes.wintypes
import gc
from PySide6.QtWidgets import QMessageBox

# ─────────────────────────────────────────────────────────────
# Estructura de Windows para GlobalMemoryStatusEx
# ─────────────────────────────────────────────────────────────

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.wintypes.DWORD),
        ("dwMemoryLoad", ctypes.wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


class SystemMonitor:
    """Monitoreo de recursos del sistema para prevenir congelamientos."""

    # Umbrales de advertencia (en MB)
    UMBRAL_ADVERTENCIA_MB = 1024  # 1 GB
    UMBRAL_CRITICO_MB = 512       # 512 MB

    # Tamaño de lote por defecto (archivos por lote)
    BATCH_SIZE_NORMAL = 50
    BATCH_SIZE_LOW_RAM = 10
    BATCH_SIZE_CRITICAL = 2

    @staticmethod
    def get_memory_info():
        """
        Obtiene información de memoria del sistema usando la API de Windows.
        """
        try:
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))

            total_mb = stat.ullTotalPhys / (1024 * 1024)
            available_mb = stat.ullAvailPhys / (1024 * 1024)
            used_percent = stat.dwMemoryLoad

            return {
                "total_mb": round(total_mb, 1),
                "available_mb": round(available_mb, 1),
                "used_percent": used_percent
            }
        except Exception:
            return {
                "total_mb": 0,
                "available_mb": 0,
                "used_percent": 0
            }

    @staticmethod
    def get_available_ram_mb():
        return SystemMonitor.get_memory_info()["available_mb"]

    @staticmethod
    def get_optimal_batch_size():
        """Calcula el tamaño óptimo de lote según la RAM disponible."""
        available = SystemMonitor.get_available_ram_mb()

        if available < SystemMonitor.UMBRAL_CRITICO_MB:
            return SystemMonitor.BATCH_SIZE_CRITICAL
        elif available < SystemMonitor.UMBRAL_ADVERTENCIA_MB:
            return SystemMonitor.BATCH_SIZE_LOW_RAM
        else:
            return SystemMonitor.BATCH_SIZE_NORMAL

    @staticmethod
    def get_memory_level():
        available = SystemMonitor.get_available_ram_mb()
        if available < SystemMonitor.UMBRAL_CRITICO_MB:
            return "critical"
        elif available < SystemMonitor.UMBRAL_ADVERTENCIA_MB:
            return "low"
        return "normal"

    @staticmethod
    def force_garbage_collection():
        gc.collect()

    @staticmethod
    def check_and_warn(parent_widget):
        """
        Verifica la RAM y muestra un mensaje de advertencia si es baja.
        NO bloquea la operación.
        """
        level = SystemMonitor.get_memory_level()
        info = SystemMonitor.get_memory_info()

        if level == "critical":
            QMessageBox.warning(
                parent_widget,
                "⚠️ Memoria Muy Baja",
                f"La memoria disponible es muy baja ({info['available_mb']:.0f} MB libres).\n\n"
                f"La conversión se realizará en lotes pequeños de "
                f"{SystemMonitor.BATCH_SIZE_CRITICAL} archivos para evitar "
                f"congelamientos y fallos en Excel.\n\n"
                f"Esto puede hacer que el proceso sea más lento, pero es más seguro."
            )
        elif level == "low":
            QMessageBox.information(
                parent_widget,
                "ℹ️ Memoria Baja",
                f"La memoria disponible es limitada ({info['available_mb']:.0f} MB libres).\n\n"
                f"Se procesarán los archivos en lotes de "
                f"{SystemMonitor.BATCH_SIZE_LOW_RAM} para un rendimiento óptimo."
            )

        return level


def procesar_excels_en_lotes(archivos, funcion_calculo, progress_callback=None):
    """
    Procesa una lista de archivos Excel en lotes para evitar congelamientos 
    y desbordamientos de memoria con la instancia de Excel.

    Args:
        archivos: lista de rutas de archivos
        funcion_calculo: función que recibe un lote (lista) de archivos y retorna resultados
        progress_callback: función(procesados, total, mensaje) opcional
    """
    total = len(archivos)
    if total == 0:
        return []

    batch_size = SystemMonitor.get_optimal_batch_size()
    resultados = []

    archivos_procesados = 0

    for i in range(0, total, batch_size):
        lote = archivos[i:i + batch_size]
        lote_num = (i // batch_size) + 1
        total_lotes = (total + batch_size - 1) // batch_size

        if progress_callback:
            progress_callback(
                archivos_procesados, total,
                f"Procesando lote {lote_num}/{total_lotes} ({len(lote)} archivos)..."
            )

        # Procesar el lote (funcion_calculo debe aceptar una lista de rutas)
        resultado_lote = funcion_calculo(lote)
        if isinstance(resultado_lote, list):
            resultados.extend(resultado_lote)
        else:
            resultados.append(resultado_lote)
            
        archivos_procesados += len(lote)

        if progress_callback:
            progress_callback(
                archivos_procesados, total,
                f"Lote {lote_num}/{total_lotes} completado. Limpiando memoria..."
            )

        # Liberar memoria cerrando posibles COM remanentes y limpiando GC
        SystemMonitor.force_garbage_collection()

    if progress_callback:
        progress_callback(total, total, "¡Conversión completada!")

    return resultados
