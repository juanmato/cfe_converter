# writer.py — Escritura de archivos TXT en formato CSV para Memory

import os
import logging

logger = logging.getLogger(__name__)

HEADER = "Dia,Debe,Haber,Concepto,RUC,Moneda,Total,CodigoIVA,IVA,Cotizacion,Libro,Regimen,SDocumento,NDocumento"


def _asiento_a_linea(a):
    """Convierte un dict de asiento a línea CSV."""
    return (
        f"{a['dia']}"
        f",{a['debe']}"
        f",{a['haber']}"
        f",{a['concepto']}"
        f",{a['ruc']}"
        f",{a['moneda']}"
        f",{a['total']}"
        f",{a['codigo_iva']}"
        f",{a['iva']}"
        f",{a['cotizacion']}"
        f",{a['libro']}"
        f",{a['regimen']}"
        f",{a['sdocumento']}"
        f",{a['ndocumento']}"
    )


def escribir_txt(asientos, ruta_salida):
    """
    Escribe la lista de asientos al archivo TXT en formato Memory.
    Crea los directorios necesarios si no existen.
    """
    directorio = os.path.dirname(ruta_salida)
    if directorio and not os.path.exists(directorio):
        os.makedirs(directorio, exist_ok=True)

    lineas = [HEADER]
    for a in asientos:
        lineas.append(_asiento_a_linea(a))

    contenido = "\n".join(lineas)

    with open(ruta_salida, "w", encoding="utf-8", newline="") as f:
        f.write(contenido)

    logger.info(f"Archivo generado: {ruta_salida}")
    logger.info(f"  {len(asientos)} asientos escritos.")
