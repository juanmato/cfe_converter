# main.py — Entry point del conversor CFE → TXT Memory

import argparse
import logging
import os
import shutil
import sys

from reader import leer_excel
from rules import generar_asientos
from writer import escribir_txt

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Convierte archivos CFE (Excel) a TXT formato Memory.",
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Ruta al archivo CFE de entrada (.xls o .xlsx)",
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Carpeta de destino para el archivo TXT generado",
    )
    parser.add_argument(
        "--nombre", "-n",
        required=False,
        default=None,
        help="Nombre del archivo de salida (sin extensión). Si no se indica, usa el nombre del archivo de entrada.",
    )
    args = parser.parse_args()

    ruta_input = os.path.abspath(args.input)
    carpeta_output = os.path.abspath(args.output)

    if not os.path.isfile(ruta_input):
        logger.error(f"Archivo de entrada no encontrado: {ruta_input}")
        sys.exit(1)

    nombre_salida = args.nombre if args.nombre else os.path.splitext(os.path.basename(ruta_input))[0]
    ruta_txt = os.path.join(carpeta_output, f"{nombre_salida}.txt")

    logger.info(f"Leyendo archivo CFE: {ruta_input}")
    registros = leer_excel(ruta_input)

    if not registros:
        logger.error("No se encontraron registros CFE en el archivo. Proceso terminado.")
        sys.exit(1)

    logger.info(f"Se encontraron {len(registros)} comprobantes en el archivo.")

    todos_asientos = []
    errores = 0
    warnings = 0

    for idx, registro in enumerate(registros, start=1):
        asientos = generar_asientos(registro, fila_num=idx)
        if asientos:
            todos_asientos.extend(asientos)
        else:
            errores += 1

    if not todos_asientos:
        logger.error("No se generaron asientos. Revise los datos de entrada.")
        sys.exit(1)

    escribir_txt(todos_asientos, ruta_txt)

    logger.info("=" * 50)
    logger.info("RESUMEN")
    logger.info(f"  CFEs leídos:       {len(registros)}")
    logger.info(f"  Asientos generados: {len(todos_asientos)}")
    if errores:
        logger.info(f"  CFEs con error:    {errores}")
    logger.info(f"  Archivo de salida: {ruta_txt}")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
