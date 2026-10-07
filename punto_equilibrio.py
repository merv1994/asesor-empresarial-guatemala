import math
import matplotlib.pyplot as plt


def calcular_punto_equilibrio(
    costos_fijos,
    precio_unitario,
    costo_variable
):
    margen_unitario = precio_unitario - costo_variable

    if costos_fijos <= 0:
        raise ValueError(
            "Los costos fijos deben ser mayores que cero."
        )

    if precio_unitario <= 0:
        raise ValueError(
            "El precio de venta debe ser mayor que cero."
        )

    if costo_variable < 0:
        raise ValueError(
            "El costo variable no puede ser negativo."
        )

    if margen_unitario <= 0:
        raise ValueError(
            "El precio de venta debe ser mayor que "
            "el costo variable por unidad."
        )

    unidades_equilibrio = costos_fijos / margen_unitario
    unidades_minimas = math.ceil(unidades_equilibrio)
    ventas_equilibrio = unidades_equilibrio * precio_unitario

    return {
        "unidades_exactas": unidades_equilibrio,
        "unidades_minimas": unidades_minimas,
        "ventas_equilibrio": ventas_equilibrio,
        "margen_unitario": margen_unitario
    }


def crear_grafico_equilibrio(
    costos_fijos,
    precio_unitario,
    costo_variable
):
    resultado = calcular_punto_equilibrio(
        costos_fijos,
        precio_unitario,
        costo_variable
    )

    unidades_equilibrio = resultado["unidades_exactas"]
    ventas_equilibrio = resultado["ventas_equilibrio"]

    limite_unidades = max(
        math.ceil(unidades_equilibrio * 1.6),
        10
    )

    unidades = list(range(limite_unidades + 1))

    ingresos = [
        unidad * precio_unitario
        for unidad in unidades
    ]

    costos_totales = [
        costos_fijos + unidad * costo_variable
        for unidad in unidades
    ]

    figura, eje = plt.subplots(figsize=(9, 5))

    eje.plot(
        unidades,
        ingresos,
        label="Ingresos",
        color="#2F6B5F",
        linewidth=2.5
    )

    eje.plot(
        unidades,
        costos_totales,
        label="Costos totales",
        color="#C79528",
        linewidth=2.5
    )

    eje.axvline(
        unidades_equilibrio,
        color="#555555",
        linestyle="--",
        linewidth=1.5,
        label="Punto de equilibrio"
    )

    eje.scatter(
        [unidades_equilibrio],
        [ventas_equilibrio],
        color="#B33A3A",
        s=75,
        zorder=5
    )

    eje.annotate(
        (
            f"{resultado['unidades_minimas']} unidades\n"
            f"Q{ventas_equilibrio:,.2f}"
        ),
        xy=(unidades_equilibrio, ventas_equilibrio),
        xytext=(12, 12),
        textcoords="offset points",
        fontsize=9
    )

    eje.set_title("Punto de equilibrio")
    eje.set_xlabel("Unidades vendidas")
    eje.set_ylabel("Monto en quetzales")
    eje.legend()
    eje.grid(alpha=0.25)

    figura.tight_layout()

    return figura, resultado