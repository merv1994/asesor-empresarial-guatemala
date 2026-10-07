import re
import streamlit as st
import graphviz
import matplotlib.pyplot as plt

from punto_equilibrio import crear_grafico_equilibrio
from pathlib import Path
from io import BytesIO
from html import unescape
from xml.sax.saxutils import escape

from openai import OpenAI
from docx import Document
from pypdf import PdfReader

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm

from reportlab.platypus import (
    Image,
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    KeepTogether,
    Image
)
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

@st.cache_data
def cargar_tesis():
    ruta = Path("documentos/tesis.docx")
    documento = Document(ruta)

    parrafos = [
        p.text.strip()
        for p in documento.paragraphs
        if len(p.text.strip()) > 40
    ]

    return parrafos


def buscar_en_tesis(consulta, parrafos, limite=8):
    palabras = set(
        re.findall(r"\w+", consulta.lower())
    )

    resultados = []

    for parrafo in parrafos:
        texto = parrafo.lower()
        puntuacion = sum(
            1 for palabra in palabras
            if len(palabra) > 3 and palabra in texto
        )

        if puntuacion > 0:
            resultados.append((puntuacion, parrafo))

    resultados.sort(reverse=True)
    return "\n\n".join(
        parrafo for _, parrafo in resultados[:limite]
    )
@st.cache_data
def cargar_fuentes_oficiales():
    carpeta = Path("documentos/fuentes oficiales")
    documentos = []

    for archivo in carpeta.rglob("*.pdf"):
        lector = PdfReader(archivo)

        for numero_pagina, pagina in enumerate(lector.pages, start=1):
            texto = pagina.extract_text() or ""

            if len(texto.strip()) > 40:
                documentos.append({
                    "texto": texto.strip(),
                    "fuente": archivo.name,
                    "pagina": numero_pagina
                })

    return documentos


def buscar_en_fuentes(consulta, documentos, limite=6):
    palabras = set(re.findall(r"\w+", consulta.lower()))
    resultados = []

    for documento in documentos:
        texto_minusculas = documento["texto"].lower()

        puntuacion = sum(
            1
            for palabra in palabras
            if len(palabra) > 3 and palabra in texto_minusculas
        )

        if puntuacion > 0:
            resultados.append((puntuacion, documento))

    resultados.sort(key=lambda resultado: resultado[0], reverse=True)

    fragmentos = []

    for _, documento in resultados[:limite]:
        fragmentos.append(
            f"Fuente: {documento['fuente']}, "
            f"página {documento['pagina']}\n"
            f"{documento['texto']}"
        )
    busqueda = (
    actividad + " "
    + formalizacion + " "
    + objetivo + " "
    + objetivo + " "
    + objetivo + " "
    + problema
)
    return "\n\n".join(fragmentos)


fuentes_oficiales = cargar_fuentes_oficiales()


parrafos_tesis = cargar_tesis()
def crear_organigrama(
    nombre_negocio,
    actividad,
    propietarios,
    empleados,
    canales
):
    organigrama = graphviz.Digraph()

    organigrama.attr(
        rankdir="TB",
        bgcolor="transparent"
    )

    organigrama.attr(
        "node",
        shape="box",
        style="rounded,filled",
        color="#2F6B5F",
        fillcolor="#E8F3EF",
        fontname="Arial"
    )

    negocio = nombre_negocio or "Mi negocio"
    actividad_texto = actividad.lower()

    organigrama.node(
        "direccion",
        f"{negocio}\nDirección general"
    )

    # Áreas administrativas comunes
    areas = {
        "administracion": "Administración y finanzas",
        "ventas": "Ventas y marketing",
        "clientes": "Servicio al cliente"
    }

    # Áreas según el tipo de negocio
    if any(
        palabra in actividad_texto
        for palabra in ["restaurante", "comida", "postre", "panadería"]
    ):
        areas.update({
            "produccion": "Producción y cocina",
            "compras": "Compras e inventario",
            "calidad": "Calidad e higiene"
        })

    elif any(
        palabra in actividad_texto
        for palabra in ["ropa", "tienda", "calzado", "accesorios"]
    ):
        areas.update({
            "inventario": "Compras e inventario",
            "ventas_local": "Ventas y atención",
            "logistica": "Pedidos y entregas"
        })

    elif any(
        palabra in actividad_texto
        for palabra in ["software", "tecnología", "sistemas", "programación"]
    ):
        areas.update({
            "desarrollo": "Desarrollo tecnológico",
            "soporte": "Soporte técnico",
            "proyectos": "Gestión de proyectos"
        })

    elif any(
        palabra in actividad_texto
        for palabra in ["agricultura", "frutas", "verduras", "cultivo"]
    ):
        areas.update({
            "produccion": "Producción agrícola",
            "calidad": "Control de calidad",
            "distribucion": "Logística y distribución"
        })

    elif any(
        palabra in actividad_texto
        for palabra in ["servicio", "consultoría", "asesoría"]
    ):
        areas.update({
            "operaciones": "Prestación del servicio",
            "proyectos": "Gestión de clientes y proyectos"
        })

    else:
        areas["operaciones"] = "Operaciones"

    # Agregar comercio digital cuando corresponda
    canales_digitales = {
        "Facebook",
        "Instagram",
        "WhatsApp",
        "Página web"
    }

    if any(canal in canales_digitales for canal in canales):
        areas["digital"] = "Comercio y comunicación digital"

    # Crear nodos y conexiones
    for identificador, nombre_area in areas.items():
        organigrama.node(
            identificador,
            nombre_area
        )
        organigrama.edge(
            "direccion",
            identificador
        )

    # Nota educativa según empleados
    if empleados == 0:
        nota = (
            "El propietario asume inicialmente\n"
            "todas estas funciones"
        )
    elif empleados == 1:
        nota = (
            "Distribuir funciones entre\n"
            "propietario y colaborador"
        )
    else:
        nota = (
            f"Distribuir responsabilidades entre\n"
            f"{empleados} colaboradores"
        )

    organigrama.node(
        "nota",
        nota,
        shape="note",
        fillcolor="#FFF4D6",
        color="#C79528"
    )

    organigrama.edge(
        "direccion",
        "nota",
        style="dashed"
    )

    return organigrama

st.title("Asesor Empresarial Guatemala")
st.subheader("Orientación para formalizar y desarrollar tu negocio")

st.info(
    "Este sistema brinda orientación general y no sustituye "
    "la asesoría de un contador o abogado."
)
def crear_pdf_analisis(
    nombre_negocio,
    actividad,
    ubicacion,
    ventas,
    gastos,
    texto_respuesta,
    grafico_equilibrio_pdf=None,
    resultado_equilibrio=None
):
    buffer = BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Diagnóstico empresarial"
    )

    estilos = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "TituloInforme",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        textColor=HexColor("#2F6B5F"),
        alignment=TA_CENTER,
        spaceAfter=20
    )

    encabezado = ParagraphStyle(
        "EncabezadoInforme",
        parent=estilos["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=HexColor("#2F6B5F"),
        spaceBefore=14,
        spaceAfter=8
    )

    cuerpo = ParagraphStyle(
        "CuerpoInforme",
        parent=estilos["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=HexColor("#30323D"),
        spaceAfter=7
    )

    lista = ParagraphStyle(
        "ListaInforme",
        parent=cuerpo,
        leftIndent=14,
        firstLineIndent=-8,
        bulletIndent=4
    )

    celda = ParagraphStyle(
        "CeldaInforme",
        parent=cuerpo,
        fontSize=8,
        leading=10,
        spaceAfter=0
    )

    celda_encabezado = ParagraphStyle(
        "CeldaEncabezado",
        parent=celda,
        fontName="Helvetica-Bold",
        textColor=colors.white,
        alignment=TA_CENTER
    )

    contenido = []

    contenido.append(
        Paragraph("Asesor Empresarial Guatemala", titulo)
    )

    contenido.append(
        Paragraph("Informe de diagnóstico empresarial", encabezado)
    )

    datos_negocio = [
        [
            Paragraph("<b>Dato</b>", celda_encabezado),
            Paragraph("<b>Información</b>", celda_encabezado)
        ],
        [
            Paragraph("Negocio", celda),
            Paragraph(escape(nombre_negocio or "Sin nombre"), celda)
        ],
        [
            Paragraph("Actividad", celda),
            Paragraph(escape(actividad), celda)
        ],
        [
            Paragraph("Ubicación", celda),
            Paragraph(escape(ubicacion), celda)
        ],
        [
            Paragraph("Ventas mensuales", celda),
            Paragraph(f"Q{ventas:,.2f}", celda)
        ],
        [
            Paragraph("Gastos mensuales", celda),
            Paragraph(f"Q{gastos:,.2f}", celda)
        ]
    ]

    tabla_datos = Table(
        datos_negocio,
        colWidths=[4.2 * cm, 12 * cm],
        repeatRows=1
    )

    tabla_datos.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2F6B5F")),
            ("BACKGROUND", (0, 1), (0, -1), HexColor("#E8F3EF")),
            ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#B7C9C2")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    contenido.append(tabla_datos)
    contenido.append(Spacer(1, 16))
    contenido.append(
        Paragraph("Análisis y recomendaciones", encabezado)
    )

    texto_limpio = unescape(texto_respuesta)

    reemplazos = {
        "<br>": "\n",
        "<br/>": "\n",
        "<br />": "\n",
        "‑": "-",
        "–": "-",
        "—": "-"
    }

    for anterior, nuevo in reemplazos.items():
        texto_limpio = texto_limpio.replace(anterior, nuevo)

    lineas = texto_limpio.splitlines()
    indice = 0

    while indice < len(lineas):
        linea = lineas[indice].strip()

        if not linea:
            indice += 1
            continue

        # Eliminar separadores Markdown
        if linea in {"---", "***", "___"}:
            indice += 1
            continue

        # Convertir tablas Markdown en tablas PDF reales
        if linea.startswith("|") and linea.endswith("|"):
            filas = []

            while indice < len(lineas):
                fila_texto = lineas[indice].strip()

                if not (
                    fila_texto.startswith("|")
                    and fila_texto.endswith("|")
                ):
                    break

                celdas = [
                    celda_texto.strip()
                    for celda_texto in fila_texto.strip("|").split("|")
                ]

                es_separador = all(
                    set(celda_texto.replace(":", "")) <= {"-"}
                    for celda_texto in celdas
                )

                if not es_separador:
                    estilo_fila = (
                        celda_encabezado if not filas else celda
                    )

                    filas.append([
                        Paragraph(
                            escape(celda_texto.replace("**", "")),
                            estilo_fila
                        )
                        for celda_texto in celdas
                    ])

                indice += 1

            if filas:
                cantidad_columnas = len(filas[0])
                ancho_total = 16.2 * cm
                ancho_columna = ancho_total / cantidad_columnas

                tabla = Table(
                    filas,
                    colWidths=[
                        ancho_columna
                        for _ in range(cantidad_columnas)
                    ],
                    repeatRows=1,
                    splitByRow=1
                )

                tabla.setStyle(
                    TableStyle([
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            HexColor("#2F6B5F")
                        ),
                        (
                            "BACKGROUND",
                            (0, 1),
                            (-1, -1),
                            HexColor("#F5F8F7")
                        ),
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.4,
                            HexColor("#B7C9C2")
                        ),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ])
                )

                contenido.append(Spacer(1, 6))
                contenido.append(tabla)
                contenido.append(Spacer(1, 10))

            continue

        # Encabezados Markdown
        if linea.startswith("### "):
            contenido.append(
                Paragraph(
                    escape(linea[4:].replace("**", "")),
                    encabezado
                )
            )

        elif linea.startswith("## "):
            contenido.append(
                Paragraph(
                    escape(linea[3:].replace("**", "")),
                    encabezado
                )
            )

        elif linea.startswith("# "):
            contenido.append(
                Paragraph(
                    escape(linea[2:].replace("**", "")),
                    encabezado
                )
            )

        # Listas
        elif linea.startswith("- "):
            contenido.append(
                Paragraph(
                    "• " + escape(
                        linea[2:].replace("**", "")
                    ),
                    lista
                )
            )

        else:
            texto_parrafo = linea.replace("**", "")

            contenido.append(
                Paragraph(
                    escape(texto_parrafo),
                    cuerpo
                )
            )

        indice += 1
    if (
    grafico_equilibrio_pdf is not None
    and resultado_equilibrio is not None
):
        contenido.append(Spacer(1, 16))

    contenido.append(
        Paragraph(
            "Punto de equilibrio",
            encabezado
        )
    )

    datos_equilibrio = [
        [
            Paragraph("<b>Indicador</b>", celda_encabezado),
            Paragraph("<b>Resultado</b>", celda_encabezado)
        ],
        [
            Paragraph("Unidades mínimas", celda),
            Paragraph(
                (
                    f"{resultado_equilibrio['unidades_minimas']} "
                    "unidades"
                ),
                celda
            )
        ],
        [
            Paragraph("Ventas necesarias", celda),
            Paragraph(
                (
                    f"Q"
                    f"{resultado_equilibrio['ventas_equilibrio']:,.2f}"
                ),
                celda
            )
        ],
        [
            Paragraph("Margen por unidad", celda),
            Paragraph(
                (
                    f"Q"
                    f"{resultado_equilibrio['margen_unitario']:,.2f}"
                ),
                celda
            )
        ]
    ]

    tabla_equilibrio = Table(
        datos_equilibrio,
        colWidths=[7.5 * cm, 8.7 * cm],
        repeatRows=1
    )

    tabla_equilibrio.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                HexColor("#2F6B5F")
            ),
            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                HexColor("#F5F8F7")
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                HexColor("#B7C9C2")
            ),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    contenido.append(tabla_equilibrio)
    contenido.append(Spacer(1, 12))

    grafico_equilibrio_pdf.seek(0)

    imagen_equilibrio = Image(
        grafico_equilibrio_pdf,
        width=16 * cm,
        height=8.9 * cm
    )

    imagen_equilibrio.hAlign = "CENTER"

    contenido.append(imagen_equilibrio)
    contenido.append(Spacer(1, 8))

    contenido.append(
        Paragraph(
            "Estimación elaborada a partir de los costos, "
            "el precio de venta y el costo variable "
            "proporcionados por el usuario.",
            cuerpo
        )
    )
    contenido.append(PageBreak())
    contenido.append(
        Paragraph("Fuentes consultadas", encabezado)
    )

    fuentes = [
        "Tesis del autor como fundamento metodológico.",
        "Manual oficial de inscripción RTU y NIT de SAT.",
        "Portal RTU Digital de SAT.",
        "Documentos oficiales del Registro Mercantil.",
        "Requisitos para sociedades de emprendimiento."
    ]

    for fuente in fuentes:
        contenido.append(
            Paragraph("• " + escape(fuente), lista)
        )

    contenido.append(Spacer(1, 16))

    contenido.append(
        Paragraph(
            "<b>Importante:</b> Este informe brinda orientación "
            "general y no sustituye la asesoría de un contador, "
            "auditor o abogado. Los trámites deben confirmarse "
            "directamente con las instituciones competentes.",
            cuerpo
        )
    )

    documento.build(contenido)

    buffer.seek(0)
    return buffer.getvalue()


    contenido.append(PageBreak())
    contenido.append(
        Paragraph("Fuentes consultadas", encabezado)
    )

    fuentes = [
        "Tesis del autor como fundamento metodológico.",
        "Manual oficial de inscripción RTU y NIT de SAT.",
        "Portal RTU Digital de SAT.",
        "Documentos oficiales del Registro Mercantil.",
        "Requisitos para sociedades de emprendimiento."
    ]

    for fuente in fuentes:
        contenido.append(
            Paragraph("• " + escape(fuente), lista)
        )

    contenido.append(Spacer(1, 16))

    contenido.append(
        Paragraph(
            "<b>Importante:</b> Este informe brinda orientación "
            "general y no sustituye la asesoría de un contador, "
            "auditor o abogado. Los trámites deben confirmarse "
            "directamente con las instituciones competentes.",
            cuerpo
        )
    )

    documento.build(contenido)

    buffer.seek(0)
    return buffer.getvalue()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    estilos = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "TituloPersonalizado",
        parent=estilos["Title"],
        textColor=HexColor("#2F6B5F"),
        alignment=TA_CENTER,
        spaceAfter=18
    )

    subtitulo = ParagraphStyle(
        "SubtituloPersonalizado",
        parent=estilos["Heading2"],
        textColor=HexColor("#2F6B5F"),
        spaceBefore=12,
        spaceAfter=8
    )

    cuerpo = ParagraphStyle(
        "CuerpoPersonalizado",
        parent=estilos["BodyText"],
        fontSize=10,
        leading=15,
        spaceAfter=8
    )

    contenido = []

    contenido.append(
        Paragraph("Informe de diagnóstico empresarial", titulo)
    )

    datos = [
        f"<b>Negocio:</b> {escape(nombre_negocio or 'Sin nombre')}",
        f"<b>Actividad:</b> {escape(actividad)}",
        f"<b>Ubicación:</b> {escape(ubicacion)}",
        f"<b>Ventas mensuales:</b> Q{ventas:,.2f}",
        f"<b>Gastos mensuales:</b> Q{gastos:,.2f}"
    ]

    for dato in datos:
        contenido.append(Paragraph(dato, cuerpo))

    contenido.append(Spacer(1, 12))
    contenido.append(
        Paragraph("Análisis y recomendaciones", subtitulo)
    )

    texto_limpio = unescape(texto_respuesta)

    reemplazos = {
        "### ": "",
        "## ": "",
        "# ": "",
        "**": "",
        "<br>": "\n",
        "<br/>": "\n",
        "<br />": "\n",
        "‑": "-",
        "–": "-",
        "—": "-"
    }

    for anterior, nuevo in reemplazos.items():
        texto_limpio = texto_limpio.replace(anterior, nuevo)

    for bloque in texto_limpio.split("\n"):
        bloque = bloque.strip()

        if bloque:
            contenido.append(
                Paragraph(escape(bloque), cuerpo)
            )

    contenido.append(PageBreak())
    contenido.append(
        Paragraph("Fuentes consultadas", subtitulo)
    )

    fuentes = [
        "Tesis del autor como fundamento metodológico.",
        "Manual oficial de inscripción RTU y NIT de SAT.",
        "Portal RTU Digital de SAT.",
        "Documentos oficiales del Registro Mercantil.",
        "Requisitos para sociedades de emprendimiento."
    ]

    for fuente in fuentes:
        contenido.append(
            Paragraph(f"- {escape(fuente)}", cuerpo)
        )

    contenido.append(Spacer(1, 15))

    contenido.append(
        Paragraph(
            "Este informe brinda orientación general y no sustituye "
            "la asesoría de un contador, auditor o abogado.",
            cuerpo
        )
    )

    documento.build(contenido)

    buffer.seek(0)
    return buffer.getvalue()

with st.form("diagnostico_empresarial"):
    st.subheader("Información del negocio")

    nombre_negocio = st.text_input(
        "Nombre del negocio"
    )

    actividad = st.text_area(
        "¿Qué productos o servicios ofrece?"
    )

    ubicacion = st.text_input(
        "Departamento y municipio"
    )

    antiguedad = st.selectbox(
        "¿Cuánto tiempo lleva funcionando?",
        [
            "Todavía no ha comenzado",
            "Menos de 6 meses",
            "Entre 6 meses y 1 año",
            "Entre 1 y 3 años",
            "Más de 3 años"
        ]
    )

    formalizacion = st.selectbox(
        "Situación actual del negocio",
        [
            "Todavía no he comenzado",
            "Funciona de manera informal",
            "Tengo NIT",
            "Estoy parcialmente formalizado",
            "Está completamente formalizado",
            "No estoy seguro"
        ]
    )

    propietarios = st.number_input(
        "Cantidad de propietarios",
        min_value=1,
        step=1
    )

    empleados = st.number_input(
        "Cantidad de empleados",
        min_value=0,
        step=1
    )

    ventas = st.number_input(
        "Ventas mensuales aproximadas en quetzales",
        min_value=0.0,
        step=100.0
    )

    gastos = st.number_input(
        "Gastos mensuales aproximados en quetzales",
        min_value=0.0,
        step=100.0
    )

    canales = st.multiselect(
        "¿Dónde realiza sus ventas?",
        [
            "Local físico",
            "Facebook",
            "Tiktok",
            "Instagram",
            "WhatsApp",
            "Página web",
            "Mercados o ferias",
            "Ventas a domicilio",
            "Otro"
        ]
    )

    problema = st.text_area(
        "¿Cuál es el principal problema del negocio?",
        placeholder=(
            "Ejemplo: Tengo una tienda de ropa, ya poseo NIT, "
            "pero desconozco cómo registrarla como empresa mercantil."
        )
    )

    st.caption(
        "Describe tu situación de la forma más clara, exacta y específica "
        "posible. Incluye qué deseas resolver y los datos relevantes. "
        "Esto permitirá generar una orientación más precisa."
    )
    st.subheader("Punto de equilibrio opcional")

    calcular_equilibrio = st.checkbox(
        "Deseo calcular y visualizar el punto de equilibrio"
    )

    st.caption(
        "Completa los siguientes datos únicamente si deseas calcular "
        "el punto de equilibrio."
    )

    costos_fijos = st.number_input(
        "Costos fijos mensuales en quetzales",
        min_value=0.0,
        step=100.0,
        help=(
            "Ejemplos: alquiler, salarios fijos, internet, "
            "licencias y servicios administrativos."
        )
    )

    precio_unitario = st.number_input(
        "Precio de venta por unidad",
        min_value=0.0,
        step=1.0,
        help="Precio cobrado por cada producto o servicio."
    )

    costo_variable = st.number_input(
        "Costo variable por unidad",
        min_value=0.0,
        step=1.0,
        help=(
            "Costo asociado directamente con cada unidad vendida, "
            "como materia prima, empaque o comisión."
        )
    )
    st.caption(
        "Los costos fijos se mantienen aunque no haya ventas. "
        "El costo variable aumenta con cada producto o servicio vendido."
    )
    objetivo = st.selectbox(
        "Objetivo principal",
        [
            "Obtener NIT",
            "Inscribir una empresa",
            "Formalizar completamente el negocio",
            "Organizar las finanzas",
            "Mejorar las ventas",
            "Recibir un diagnóstico completo"
        ]
    )

    enviado = st.form_submit_button(
        "Analizar mi negocio"
    )

if enviado:
    if not actividad.strip():
        st.warning("Describe primero la actividad de tu negocio.")
    else:
        busqueda = (
    actividad + " "
    + formalizacion + " "
    + objetivo + " "
    + problema + " "
    + "formalización finanzas ventas costos empresa SAT Registro Mercantil"
) 

        contexto_tesis = buscar_en_tesis(
            busqueda,
            parrafos_tesis
        )
        contexto_oficial = buscar_en_fuentes(
    busqueda,
    fuentes_oficiales
)

        consulta = f"""
Actúa como consultor empresarial y financiero para emprendedores de Guatemala.

DATOS DEL NEGOCIO

Nombre: {nombre_negocio}
Actividad económica: {actividad}
Ubicación: {ubicacion}
Tiempo funcionando: {antiguedad}
Situación de formalización: {formalizacion}
Cantidad de propietarios: {propietarios}
Cantidad de empleados: {empleados}
Ventas mensuales aproximadas: Q{ventas:,.2f}
Gastos mensuales aproximados: Q{gastos:,.2f}
Canales de venta: {", ".join(canales) if canales else "No especificados"}
Problema principal: {problema}
Objetivo: {objetivo}

INFORMACIÓN RECUPERADA DE LA TESIS

{contexto_tesis}

INSTRUCCIONES

Utiliza la tesis como fundamento metodológico, pero no copies literalmente.
No inventes leyes, montos, requisitos ni procedimientos oficiales.

Genera:

1. Resumen ejecutivo.
2. Diagnóstico del estado actual.
3. Análisis financiero básico.
4. Fortalezas, oportunidades, debilidades y amenazas.
5. Ruta general de formalización.
6. Estrategia personalizada para aumentar las ventas.
7. Plan de acción dividido en corto, mediano y largo plazo.
8. Riesgos y aspectos que requieren atención profesional.

Aclara que los trámites deben verificarse directamente con SAT,
Registro Mercantil y profesionales acreditados.
FUENTES OFICIALES RECUPERADAS

{contexto_oficial}

Utiliza estas fuentes para orientar sobre trámites y requisitos.
Menciona el nombre del documento y la página utilizada.
Si las fuentes no contienen la respuesta, indícalo claramente.
No inventes requisitos, costos, leyes ni procedimientos.
Utiliza únicamente fuentes relacionadas directamente con el objetivo.
Si el objetivo es obtener NIT, no incluyas sociedades ni aranceles
del Registro Mercantil, salvo que sean necesarios y lo justifiques.
Cuando menciones una tabla, reproduce solamente sus datos relevantes.
Al final incluye una sección llamada "Fundamento del análisis".
Explica brevemente qué recomendaciones se apoyan en la tesis y cuáles
proceden de documentos oficiales. No inventes capítulos ni páginas
de la tesis si esa información no está disponible.
"""




        try:
            with st.spinner("Analizando tu negocio..."):
                                respuesta = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Responde claramente en español usando únicamente Markdown. "
                                "No utilices HTML, LaTeX, fórmulas con barras invertidas, "
                                "etiquetas <br> ni símbolos matemáticos especiales. "
                                "Expresa todos los cálculos en texto simple. "
                                "Ejemplo: (Q2,000 - Q1,000) / Q2,000 = 50 %. "
                                "Para listas utiliza guiones y para tablas utiliza Markdown."
                            )
                        },
                        {
                            "role": "user",
                            "content": consulta
                        }
                    ],
                    max_tokens=5000
                )

            motivo = respuesta.choices[0].finish_reason

            if motivo == "length":
                st.warning(
                    "La respuesta alcanzó el límite y podría estar incompleta."
                )

            texto_respuesta = respuesta.choices[0].message.content

            texto_respuesta = (
                texto_respuesta
                .replace("&lt;br&gt;", "\n")
                .replace("&lt;brrespuesta = client.chat/&gt;", "\n")
                .replace("&lt;br /&gt;", "\n")
                .replace("<br>", "\n")
                .replace("<br/>", "\n")
                .replace("<br />", "\n")
                .replace("\\[", "")
                .replace("\\]", "")
                .replace("\\(", "")
                .replace("\\)", "")
                .replace("\\,", " ")
                .replace("\\%", "%")
            )

            st.success("Diagnóstico completado")
            st.markdown(texto_respuesta)
            grafico_equilibrio_pdf = None
            resultado_equilibrio = None
            figura_equilibrio = None

            if calcular_equilibrio:
                try:
                    figura_equilibrio, resultado_equilibrio = (
                        crear_grafico_equilibrio(
                            costos_fijos,
                            precio_unitario,
                            costo_variable
                        )
                    )

                    st.subheader("Gráfico del punto de equilibrio")

                    columna_1, columna_2, columna_3 = st.columns(3)

                    columna_1.metric(
                        "Unidades mínimas",
                        (
                            f"{resultado_equilibrio['unidades_minimas']} "
                            "unidades"
                        )
                    )

                    columna_2.metric(
                        "Ventas necesarias",
                        (
                            f"Q"
                            f"{resultado_equilibrio['ventas_equilibrio']:,.2f}"
                        )
                    )

                    columna_3.metric(
                        "Margen por unidad",
                        (
                            f"Q"
                            f"{resultado_equilibrio['margen_unitario']:,.2f}"
                        )
                    )

                    st.pyplot(
                        figura_equilibrio,
                        width="stretch"
                    )
                    grafico_equilibrio_pdf = BytesIO()

                    figura_equilibrio.savefig(
                        grafico_equilibrio_pdf,
                        format="png",
                        dpi=180,
                        bbox_inches="tight",
                        facecolor="white"
                    )

                    grafico_equilibrio_pdf.seek(0)

                    plt.close(figura_equilibrio)

                    st.caption(
                        "Este cálculo es una estimación basada en los "
                        "costos, el precio y los datos proporcionados."
                    )

                except ValueError as error_equilibrio:
                    st.warning(
                        "No fue posible calcular el punto de equilibrio: "
                        + str(error_equilibrio)
                    )
            pdf_generado = crear_pdf_analisis(
                nombre_negocio,
                actividad,
                ubicacion,
                ventas,
                gastos,
                texto_respuesta,
                grafico_equilibrio_pdf,
                resultado_equilibrio
            )

            st.download_button(
                label="Descargar diagnóstico en PDF",
                data=pdf_generado,
                file_name="diagnostico_empresarial.pdf",
                mime="application/pdf",
                icon=":material/download:"
            )
            st.subheader("Organigrama recomendado")

            organigrama = crear_organigrama(
    nombre_negocio,
    actividad,
    propietarios,
    empleados,
    canales
)

            st.graphviz_chart(
                organigrama,
                width="stretch"
            )

            if empleados == 0:
                st.info(
                    "Aunque actualmente una sola persona realice todas "
                    "las actividades, separar las funciones ayuda a "
                    "organizar el negocio y prepararlo para crecer."
                )

            st.subheader("Fuentes consultadas")

            st.markdown(
                """
- ### Fuente metodológica

- **BENEFICIOS DE LA FORMALIZACIÓN E INSCRIPCIÓN DE EMPRESAS E-COMMERCE DEDICADAS A LA VENTA DE ALIMENTOS PREPARADOS, A TRAVÉS DE INTERNET, EN LA CABECERA MUNICIPAL DE HUEHUETENANGO, REALIZADO POR EL ESTUDIANTE MILTON EDUARDO RECINOS VILLATORO:** documento base utilizado para el diagnóstico empresarial, los fundamentos de la inscripción de empresas y la orientación metodológica.

### Fuentes oficiales
- [Manual oficial de inscripción RTU y NIT](https://cdn.c.sat.gob.gt/resources/instructivos/Instructivo-RTU-Inscripci%C3%B3n.pdf)
- [Portal RTU Digital de SAT](https://portal.sat.gob.gt/portal/rtu-digital/)
- [Requisitos de sociedades de emprendimiento](https://principal.registromercantil.gob.gt/wp-content/uploads/2024/01/34-REQUISITOS-INSCRIPCION-DE-SOCIEDADES-EMPRENDIMIENTO.pdf)
- [Sede Virtual del Registro Mercantil](https://sedevirtual.registromercantil.gob.gt/sedevirtual/)
                """
            )

        except Exception as error:
            st.error("No fue posible generar el diagnóstico.")
            st.code(str(error))
