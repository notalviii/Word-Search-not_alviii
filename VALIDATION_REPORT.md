# Informe de validación

Fecha: 2026-09-26

## Comprobaciones realizadas

| Área | Resultado | Evidencia |
|---|---:|---|
| Compilación estática | Correcta | `compileall` sobre `main.py`, `app/` y `tests/` |
| CSV y normalización | Correcto | Minúsculas, espacios, tildes, `Ñ`, `Ü`, líneas/campos vacíos y duplicados |
| Generador | Correcto | Todas las palabras y coordenadas se verifican contra la cuadrícula |
| Direcciones y cruces | Correcto | Pruebas de dirección única, diagonales y cruces desactivados |
| Configuración JSON | Correcto | Prueba de guardado/carga y restauración de valores |
| Layout | Correcto | Márgenes y seis posiciones de cuadrícula comprobados |
| PDF | Correcto | PDF de 8 páginas A4, revisado con `pdfinfo`, `pypdf` y renderizado PNG |

## Suite automática

Comando ejecutado con Python 3.12.14:

```text
python -m unittest discover -s tests -v
```

Resultado: **12 pruebas superadas, 0 fallos**.

## Artefacto de prueba

`output/libro_prueba.pdf` se ha generado desde `examples/palabras.csv` y `examples/configuracion_animales.json`. Contiene cuatro sopas y sus cuatro soluciones, en A4, con márgenes de 15 mm y estilo de solución con círculos.

## Limitación del entorno de validación

El runtime Python integrado utilizado para validar el proyecto no tiene instalado `customtkinter`. Por ese motivo no se pudo abrir una sesión gráfica automatizada en este entorno. La interfaz compila de forma estática y `requirements.txt` declara `customtkinter`; una instalación conforme al README permite iniciar la aplicación con `python main.py` en Windows.
