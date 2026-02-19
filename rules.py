# rules.py — Reglas contables para generación de asientos desde CFE

import logging
from config import (
    PROVEEDORES, CUENTA_DEFAULT, TIPO_CFE_PREFIJOS,
    IVA_22_CUENTA, IVA_10_CUENTA, IVA_OTRO_CUENTA, IVA_TOLERANCIA,
)

logger = logging.getLogger(__name__)


def _codigo_moneda(moneda_texto):
    """Convierte moneda texto a código numérico. Retorna None si no reconocida."""
    m = moneda_texto.upper().strip()
    if m in ("UYU", "$U", "PESOS", "PESO URUGUAYO"):
        return 0
    if m in ("USD", "US$", "DÓLAR", "DOLAR"):
        return 1
    return None


def _prefijo_tipo(tipo_cfe):
    """Retorna el prefijo para el concepto según tipo CFE."""
    tipo_lower = tipo_cfe.lower().strip()
    return TIPO_CFE_PREFIJOS.get(tipo_lower)


def _cuenta_proveedor(rut, fila_num=None):
    """Busca la cuenta Debe del proveedor por RUT."""
    info = PROVEEDORES.get(rut)
    if info is None:
        logger.warning(
            f"RUT {rut} no encontrado en tabla de proveedores"
            + (f" (fila {fila_num})" if fila_num else "")
            + f". Se usa cuenta por defecto {CUENTA_DEFAULT}."
        )
        return CUENTA_DEFAULT
    return info["debe"]


def _libro(cuenta):
    """Determina Libro: 'C' si la cuenta empieza con 1, 'E' si empieza con 5."""
    s = str(cuenta)
    if s.startswith("1"):
        return "C"
    if s.startswith("5"):
        return "E"
    return "C"


def _cuenta_iva(monto_neto, iva):
    """Calcula la cuenta IVA según el porcentaje IVA/Neto."""
    if monto_neto == 0:
        return IVA_OTRO_CUENTA
    porcentaje = abs(iva / monto_neto)
    if abs(porcentaje - 0.22) <= IVA_TOLERANCIA:
        return IVA_22_CUENTA
    if abs(porcentaje - 0.10) <= IVA_TOLERANCIA:
        return IVA_10_CUENTA
    return IVA_OTRO_CUENTA


def _cuenta_cierre_debe(cod_moneda):
    """Cuenta Debe para cierre: 21111 (UYU) o 21112 (USD)."""
    return 21111 if cod_moneda == 0 else 21112


def _cuenta_cierre_haber(cod_moneda):
    """Cuenta Haber para cierre: 21111 (UYU) o 21112 (USD)."""
    return 21111 if cod_moneda == 0 else 21112


def _cuenta_banco_debe(cod_moneda):
    """Cuenta para caso Monto Neto = 0, Debe: 21111/21112."""
    return 21111 if cod_moneda == 0 else 21112


def _cuenta_banco_haber(cod_moneda):
    """Cuenta para caso Monto Neto = 0, Haber: 11121/11122."""
    return 11121 if cod_moneda == 0 else 11122


def _cuenta_resguardo_haber(cod_moneda):
    """Cuenta Haber para e-Resguardo: 11111/11112."""
    return 11111 if cod_moneda == 0 else 11112


def _formato_monto(valor):
    """Formatea un monto a 2 decimales con punto decimal."""
    return f"{valor:.2f}"


def _crear_asiento(dia, debe, haber, concepto, ruc, moneda, total, iva, libro):
    """Crea un dict representando un asiento contable."""
    return {
        "dia": dia,
        "debe": debe,
        "haber": haber,
        "concepto": concepto,
        "ruc": ruc,
        "moneda": moneda,
        "total": _formato_monto(total),
        "codigo_iva": 0,
        "iva": _formato_monto(iva),
        "cotizacion": 0,
        "libro": libro,
        "regimen": "",
        "sdocumento": "",
        "ndocumento": 0,
    }


def generar_asientos(registro, fila_num=None):
    """
    Genera los asientos contables para un registro CFE.
    Retorna una lista de dicts (asientos) o lista vacía si hay error.
    """
    tipo_cfe = registro["tipo_cfe"]
    prefijo = _prefijo_tipo(tipo_cfe)
    if prefijo is None:
        logger.error(
            f"Tipo CFE no reconocido: '{tipo_cfe}'"
            + (f" (fila {fila_num})" if fila_num else "")
            + ". Se omite."
        )
        return []

    cod_moneda = _codigo_moneda(registro["moneda"])
    if cod_moneda is None:
        logger.error(
            f"Moneda no reconocida: '{registro['moneda']}'"
            + (f" (fila {fila_num})" if fila_num else "")
            + ". Se omite."
        )
        return []

    dia = registro["fecha"].day
    serie = registro["serie"]
    numero = registro["numero"]
    rut = registro["rut_emisor"]
    concepto = f" {prefijo} {serie} {numero}"

    # Determinar tipo de procesamiento
    tipo_lower = tipo_cfe.lower().strip()

    if tipo_lower == "e-resguardo":
        return _asientos_resguardo(dia, concepto, rut, cod_moneda, registro, fila_num)
    else:
        # e-Factura o Nota de Crédito de e-Factura
        return _asientos_factura(dia, concepto, rut, cod_moneda, registro, fila_num)


def _asientos_factura(dia, concepto, rut, cod_moneda, registro, fila_num):
    """Genera asientos para e-Factura o Nota de Crédito."""
    monto_neto = registro["monto_neto"]
    iva = registro["iva_ventas"]
    monto_total = registro["monto_total"]
    asientos = []

    if monto_neto == 0:
        # CASO 1C: Monto Neto = 0 (caso especial) → 2 asientos
        cuenta_debe = _cuenta_banco_debe(cod_moneda)
        cuenta_haber = _cuenta_banco_haber(cod_moneda)

        asientos.append(_crear_asiento(
            dia=dia, debe=cuenta_debe, haber="",
            concepto=concepto, ruc=rut, moneda=cod_moneda,
            total=monto_total, iva=0.0, libro="C",
        ))
        asientos.append(_crear_asiento(
            dia=dia, debe="", haber=cuenta_haber,
            concepto=concepto, ruc=rut, moneda=cod_moneda,
            total=monto_total, iva=0.0, libro="C",
        ))
    else:
        # CASO 1A o 1B
        cuenta_debe_prov = _cuenta_proveedor(rut, fila_num)
        libro_prov = _libro(cuenta_debe_prov)

        # Asiento 1: Cuenta del proveedor
        asientos.append(_crear_asiento(
            dia=dia, debe=cuenta_debe_prov, haber="",
            concepto=concepto, ruc=rut, moneda=cod_moneda,
            total=monto_neto, iva=0.0, libro=libro_prov,
        ))

        if iva != 0:
            # CASO 1A: Con IVA → Asiento 2: IVA
            cuenta_iva = _cuenta_iva(monto_neto, iva)
            asientos.append(_crear_asiento(
                dia=dia, debe=cuenta_iva, haber="",
                concepto=concepto, ruc=rut, moneda=cod_moneda,
                total=0.0, iva=iva, libro=libro_prov,
            ))

        # Asiento 3 (o 2 si sin IVA): Cierre contrapartida
        cuenta_haber_cierre = _cuenta_cierre_haber(cod_moneda)
        asientos.append(_crear_asiento(
            dia=dia, debe="", haber=cuenta_haber_cierre,
            concepto=concepto, ruc=rut, moneda=cod_moneda,
            total=monto_total, iva=0.0, libro=libro_prov,
        ))

    return asientos


def _asientos_resguardo(dia, concepto, rut, cod_moneda, registro, fila_num):
    """Genera asientos para e-Resguardo."""
    monto_ret = registro["monto_ret_per"]
    monto_cred = registro["monto_cred_fiscal"]
    cuenta_haber = _cuenta_resguardo_haber(cod_moneda)
    asientos = []

    if monto_ret > 0:
        asientos.append(_crear_asiento(
            dia=dia, debe=11337, haber=cuenta_haber,
            concepto=concepto, ruc=rut, moneda=cod_moneda,
            total=monto_ret, iva=0.0, libro="C",
        ))

    if monto_cred > 0:
        asientos.append(_crear_asiento(
            dia=dia, debe=11336, haber=cuenta_haber,
            concepto=concepto, ruc=rut, moneda=cod_moneda,
            total=monto_cred, iva=0.0, libro="C",
        ))

    if not asientos:
        logger.warning(
            f"e-Resguardo sin montos Ret/Per ni Cred. Fiscal"
            + (f" (fila {fila_num})" if fila_num else "")
        )

    return asientos
