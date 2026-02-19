# config.py — Configuración de proveedores, cuentas y mapeo de columnas

# Cuenta contable por defecto para RUT no encontrado en la tabla
CUENTA_DEFAULT = 99999

# Tabla de proveedores: RUT -> {nombre, debe}
PROVEEDORES = {
    "080128330013": {"nombre": "FAUSTINO CARLOS", "debe": 11411},
    "090259200013": {"nombre": "FATE SISTEMAS", "debe": 5109},
    "100004430014": {"nombre": "POLAKOF Y CIA", "debe": 5117},
    "100182590018": {"nombre": "ADALBERTO CABRERA", "debe": 11411},
    "100866340013": {"nombre": "FMC SAS", "debe": 5117},
    "110166210017": {"nombre": "FERNANDO MIRANDA", "debe": 5117},
    "150015190016": {"nombre": "SUC. ROCCA", "debe": 5105},
    "150044260019": {"nombre": "GARA GARDO", "debe": 11411},
    "150051690015": {"nombre": "VET. EL GAUCHO", "debe": 5117},
    "150082360017": {"nombre": "GUSTAVO ACOSTA", "debe": 11411},
    "150092900014": {"nombre": "LUIFER", "debe": 5117},
    "150105270019": {"nombre": "SERGIO MARTIN VEIGA LOPEZ", "debe": 11411},
    "150107120014": {"nombre": "ANFERAL", "debe": 5105},
    "150131850019": {"nombre": "DON DETODO", "debe": 11411},
    "150147400018": {"nombre": "ROCHA TABACOS", "debe": 11411},
    "150160400018": {"nombre": "XIMENA SRL", "debe": 11411},
    "150161640012": {"nombre": "JULIO BAEZ", "debe": 11411},
    "150164530013": {"nombre": "SERVIMA", "debe": 11411},
    "150213670014": {"nombre": "PABLO MARCELO GABITO DIANESSI", "debe": 5117},
    "150220680011": {"nombre": "ROBINSON MOLINA", "debe": 11411},
    "150278160010": {"nombre": "TORNILLERIA DOS MIL", "debe": 5117},
    "150282390017": {"nombre": "JUAN BONARDI", "debe": 11411},
    "150285660015": {"nombre": "DIST. LARZABAL", "debe": 11411},
    "150299700014": {"nombre": "NOGUES NICOLAS, NAVARRO ANDRES Y OTROS", "debe": 5117},
    "150306120014": {"nombre": "MARIA GOMEZ", "debe": 11411},
    "150309040011": {"nombre": "ALEXANDER SOSA", "debe": 11411},
    "150341240012": {"nombre": "BERNADET MOREIRA", "debe": 11411},
    "150386160018": {"nombre": "FERNANDO DECUADRA", "debe": 5117},
    "150442450012": {"nombre": "MATIAS SILVA DE LA CRUZ", "debe": 11411},
    "150449150014": {"nombre": "BARBOZA DARIO Y RUIZ SEBASTIAN", "debe": 11411},
    "150754450018": {"nombre": "ESTUDIO LEZAMA", "debe": 5109},
    "150933960010": {"nombre": "DIST. LA LICEAL", "debe": 11411},
    "151052960014": {"nombre": "AMERICO MATO S.R.L", "debe": 11411},
    "210065430018": {"nombre": "INTERAGROVIAL S.A", "debe": 5107},
    "210166270016": {"nombre": "IND. BAHIA", "debe": 11411},
    "210182980014": {"nombre": "PONTYN S.A", "debe": 11411},
    "210232930015": {"nombre": "ALTAMA S.A", "debe": 11411},
    "210250140012": {"nombre": "DARCY S.A", "debe": 11411},
    "210465050018": {"nombre": "BSE", "debe": 5109},
    "210465260012": {"nombre": "BANCO REPÚBLICA", "debe": 5117},
    "210591790017": {"nombre": "CROMIN S.A", "debe": 5116},
    "210778720012": {"nombre": "UTE", "debe": 5110},
    "211542300018": {"nombre": "FIRST DATA", "debe": 5301},
    "212170220016": {"nombre": "FAMA LTDA", "debe": 5117},
    "212364760016": {"nombre": "ALVARO DE LEÓN", "debe": 5109},
    "212612270013": {"nombre": "FERAL S.A", "debe": 11411},
    "212661610019": {"nombre": "POHENIX", "debe": 5117},
    "212971630018": {"nombre": "VAMOS QUE VAMOS", "debe": 11411},
    "213590730015": {"nombre": "GIFAL S A", "debe": 11411},
    "213596650013": {"nombre": "VISA", "debe": 5301},
    "213731140014": {"nombre": "BEKMAR", "debe": 11411},
    "215500380016": {"nombre": "RESONANCE", "debe": 5109},
    "217291190011": {"nombre": "FLEXIS S.A", "debe": 11411},
    "217795000011": {"nombre": "EMILUPE", "debe": 11411},
    "218048550014": {"nombre": "ROCIO VALETINA RODRIGUEZ", "debe": 11411},
    "218093120015": {"nombre": "DIST. RAMIREZ", "debe": 11411},
    "218304270011": {"nombre": "SANTANDER SOLUTIONS", "debe": 5301},
    "218502340016": {"nombre": "GETNET URUGUAY S.A", "debe": 5301},
    "220452750013": {"nombre": "CEDONA SAS", "debe": 11411},
    "220476050011": {"nombre": "MAR REPUESTOS SAS", "debe": 5107},
    "220530290011": {"nombre": "FERRETERIA Y BARRACA MARCELO SAS", "debe": 5117},
}

# Aliases flexibles para nombres de columnas del Excel CFE
# Clave interna -> lista de posibles nombres (en minúsculas)
COLUMN_ALIASES = {
    "fecha_comprobante": ["fecha comprobante", "fecha_comprobante", "fecha"],
    "tipo_cfe": ["tipo cfe", "tipo_cfe", "tipo"],
    "serie": ["serie"],
    "numero": ["número", "numero", "nro", "n°", "nº"],
    "rut_emisor": ["rut emisor", "rut_emisor", "rut"],
    "moneda": ["moneda"],
    "monto_neto": ["monto neto", "monto_neto", "neto", "suma de monto neto"],
    "iva_ventas": ["iva ventas", "iva_ventas", "iva", "suma de iva ventas"],
    "monto_total": ["monto total", "monto_total", "total", "suma de monto total"],
    "monto_ret_per": [
        "monto ret/per", "monto_ret_per", "ret/per", "retención", "retencion",
        "suma de monto ret/per",
    ],
    "monto_cred_fiscal": [
        "monto cred. fiscal", "monto_cred_fiscal", "cred. fiscal",
        "credito fiscal", "crédito fiscal", "suma de monto cred. fiscal",
    ],
}

# Mapeo de tipo CFE a prefijo para el campo Concepto
TIPO_CFE_PREFIJOS = {
    "e-factura": "e-F",
    "nota de crédito de e-factura": "NC",
    "nota de credito de e-factura": "NC",
    "e-resguardo": "e-R",
}

# Cuentas IVA según porcentaje
IVA_22_CUENTA = 11331
IVA_10_CUENTA = 11332
IVA_OTRO_CUENTA = 11338

# Tolerancia para comparación de porcentaje IVA
IVA_TOLERANCIA = 0.015
