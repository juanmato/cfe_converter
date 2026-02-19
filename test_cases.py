# test_cases.py — Verificación contra los TXT de ejemplo

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from rules import generar_asientos
from writer import HEADER

def _asiento_a_linea(a):
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


def test_txt1():
    """TXT 1: e-Factura con IVA (3 asientos)"""
    registro = {
        "fecha": datetime(2026, 1, 14),
        "tipo_cfe": "e-Factura",
        "serie": "A",
        "numero": "10779",
        "rut_emisor": "080128330013",
        "moneda": "UYU",
        "monto_neto": 57373.61,
        "iva_ventas": 4616.39,
        "monto_total": 61990.0,
        "monto_ret_per": 0.0,
        "monto_cred_fiscal": 0.0,
    }
    asientos = generar_asientos(registro)
    lineas = [_asiento_a_linea(a) for a in asientos]

    esperado = [
        "14,11411,, e-F A 10779,080128330013,0,57373.61,0,0.00,0,C,,,0",
        "14,11338,, e-F A 10779,080128330013,0,0.00,0,4616.39,0,C,,,0",
        "14,,21111, e-F A 10779,080128330013,0,61990.00,0,0.00,0,C,,,0",
    ]

    print("=== TXT 1: e-Factura con IVA ===")
    ok = True
    for i, (gen, exp) in enumerate(zip(lineas, esperado)):
        match = "OK" if gen == exp else "FAIL"
        if match == "FAIL":
            ok = False
        print(f"  Asiento {i+1}: {match}")
        if gen != exp:
            print(f"    Generado: {gen}")
            print(f"    Esperado: {exp}")
    assert len(lineas) == len(esperado), f"Cantidad asientos: {len(lineas)} vs {len(esperado)}"
    return ok


def test_txt2():
    """TXT 2: e-Factura sin IVA (2 asientos)"""
    registro = {
        "fecha": datetime(2026, 1, 9),
        "tipo_cfe": "e-Factura",
        "serie": "A",
        "numero": "433541",
        "rut_emisor": "150015190016",
        "moneda": "UYU",
        "monto_neto": 2900.0,
        "iva_ventas": 0.0,
        "monto_total": 2900.0,
        "monto_ret_per": 0.0,
        "monto_cred_fiscal": 0.0,
    }
    asientos = generar_asientos(registro)
    lineas = [_asiento_a_linea(a) for a in asientos]

    # Según las reglas: RUT 150015190016 -> debe=5105 -> Libro="E"
    esperado = [
        "9,5105,, e-F A 433541,150015190016,0,2900.00,0,0.00,0,E,,,0",
        "9,,21111, e-F A 433541,150015190016,0,2900.00,0,0.00,0,E,,,0",
    ]

    print("=== TXT 2: e-Factura sin IVA ===")
    print("  NOTA: El TXT 2 de ejemplo usa cuenta 11411/Libro=C,")
    print("  pero la tabla PROVEEDORES indica debe=5105/Libro=E para RUT 150015190016.")
    print("  Seguimos la tabla PROVEEDORES (fuente autoritativa).")
    ok = True
    for i, (gen, exp) in enumerate(zip(lineas, esperado)):
        match = "OK" if gen == exp else "FAIL"
        if match == "FAIL":
            ok = False
        print(f"  Asiento {i+1}: {match}")
        if gen != exp:
            print(f"    Generado: {gen}")
            print(f"    Esperado: {exp}")
    assert len(lineas) == len(esperado), f"Cantidad asientos: {len(lineas)} vs {len(esperado)}"
    return ok


def test_txt3():
    """TXT 3: e-Factura Monto Neto = 0 (2 asientos, caso especial)"""
    registro = {
        "fecha": datetime(2026, 1, 15),
        "tipo_cfe": "e-Factura",
        "serie": "A",
        "numero": "41836",
        "rut_emisor": "150282390017",
        "moneda": "UYU",
        "monto_neto": 0.0,
        "iva_ventas": 0.0,
        "monto_total": 36255.0,
        "monto_ret_per": 0.0,
        "monto_cred_fiscal": 0.0,
    }
    asientos = generar_asientos(registro)
    lineas = [_asiento_a_linea(a) for a in asientos]

    esperado = [
        "15,21111,, e-F A 41836,150282390017,0,36255.00,0,0.00,0,C,,,0",
        "15,,11121, e-F A 41836,150282390017,0,36255.00,0,0.00,0,C,,,0",
    ]

    print("=== TXT 3: e-Factura Monto Neto = 0 ===")
    ok = True
    for i, (gen, exp) in enumerate(zip(lineas, esperado)):
        match = "OK" if gen == exp else "FAIL"
        if match == "FAIL":
            ok = False
        print(f"  Asiento {i+1}: {match}")
        if gen != exp:
            print(f"    Generado: {gen}")
            print(f"    Esperado: {exp}")
    assert len(lineas) == len(esperado), f"Cantidad asientos: {len(lineas)} vs {len(esperado)}"
    return ok


def test_txt4():
    """TXT 4: e-Resguardo (2 asientos)"""
    registro = {
        "fecha": datetime(2026, 1, 1),
        "tipo_cfe": "e-Resguardo",
        "serie": "A",
        "numero": "697190",
        "rut_emisor": "213596650013",
        "moneda": "UYU",
        "monto_neto": 0.0,
        "iva_ventas": 0.0,
        "monto_total": 0.0,
        "monto_ret_per": 2021.31,
        "monto_cred_fiscal": 1684.43,
    }
    asientos = generar_asientos(registro)
    lineas = [_asiento_a_linea(a) for a in asientos]

    # Según las reglas: ambos asientos de e-Resguardo usan prefijo "e-R"
    esperado = [
        "1,11337,11111, e-R A 697190,213596650013,0,2021.31,0,0.00,0,C,,,0",
        "1,11336,11111, e-R A 697190,213596650013,0,1684.43,0,0.00,0,C,,,0",
    ]

    print("=== TXT 4: e-Resguardo ===")
    print("  NOTA: El TXT 4 de ejemplo tiene 'e-F' en la 2da línea,")
    print("  pero la regla dice 'Mismo concepto que arriba' (e-R).")
    print("  Seguimos la regla especificada.")
    ok = True
    for i, (gen, exp) in enumerate(zip(lineas, esperado)):
        match = "OK" if gen == exp else "FAIL"
        if match == "FAIL":
            ok = False
        print(f"  Asiento {i+1}: {match}")
        if gen != exp:
            print(f"    Generado: {gen}")
            print(f"    Esperado: {exp}")
    assert len(lineas) == len(esperado), f"Cantidad asientos: {len(lineas)} vs {len(esperado)}"
    return ok


if __name__ == "__main__":
    results = []
    results.append(("TXT 1", test_txt1()))
    print()
    results.append(("TXT 2", test_txt2()))
    print()
    results.append(("TXT 3", test_txt3()))
    print()
    results.append(("TXT 4", test_txt4()))
    print()
    print("=== RESUMEN ===")
    for name, ok in results:
        print(f"  {name}: {'PASS' if ok else 'REVISAR (discrepancia con ejemplo)'}")
