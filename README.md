# Word Search Book Maker

Aplicación de escritorio para Windows que convierte un CSV en un libro de sopas de letras y sus soluciones en PDF. La aplicación mantiene la cuadrícula, las palabras y las coordenadas como datos de dominio; la solución se dibuja sobre **la misma cuadrícula**, nunca sobre una sopa regenerada.

## Requisitos e instalación

- Windows y Python 3.12 o posterior.
- `pip` actualizado.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Si PowerShell no permite activar el entorno, puede ejecutar ` .\.venv\Scripts\python.exe main.py` directamente.

## Uso

1. Pulse **CARGAR CSV** y seleccione un archivo UTF-8.
2. Configure página, márgenes, cuadrícula, direcciones y diseño.
3. Pulse **PREVISUALIZAR**. La generación ocurre fuera del hilo de la ventana.
4. Navegue entre las sopas, active *Ver solución* y use `+`/`−` para ampliar o reducir.
5. Elija la ruta de salida y pulse **GENERAR PDF**. Puede cancelar sin que se conserve un PDF incompleto.

El panel permite seleccionar `todas` las sopas, números concretos (`1,4,8`) o rangos (`1-5,9`). También permite dos órdenes: sopa/solución consecutivas o todas las sopas seguidas de todas las soluciones.

## Formato CSV

No hay cabecera. Cada línea es una sopa y cada campo separado por una coma es una palabra. Las líneas pueden tener distinta cantidad de palabras.

```csv
perro,gato,tigre,león,oso
caballo,VACA,cerdo,oveja,gallina
árbol,niño,pingüino,ÑANDÚ,camión
```

La aplicación elimina espacios externos y convierte internamente a mayúsculas: ` árbol ` pasa a `ÁRBOL`. Conserva tildes, `Ñ` y `Ü`. Antes de generar se bloquean archivos vacíos, líneas vacías, campos vacíos (incluidas comas sobrantes), duplicados dentro de la misma sopa, codificación no UTF-8 y palabras incompatibles con la cuadrícula.

Hay un archivo listo para probar en [examples/palabras.csv](examples/palabras.csv) y una configuración en [examples/configuracion_animales.json](examples/configuracion_animales.json).

## Configuración y PDF

- Los tamaños de página A4, Letter, 6 × 9 in, 8.5 × 11 in y personalizado son independientes de las filas y columnas.
- Los cuatro márgenes se editan por separado en la unidad de página activa (`mm` o `in`).
- Active direcciones individualmente; las diagonales, palabras invertidas y cruces son opciones independientes.
- *Ajustar automáticamente* calcula la casilla más grande que cabe junto con títulos y lista de palabras. Si no cabe, la aplicación comunica el error antes de exportar.
- Guarde/cargue la configuración en JSON desde la interfaz. El CSV no se altera al cargar un JSON.

El PDF se crea con ReportLab y emplea líneas, texto y marcas vectoriales. Las soluciones usan círculos, líneas o resaltados sobre las coordenadas conservadas por el generador.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

La suite cubre normalización española, CSV variable/erróneo, generación, restricciones de dirección, coordenadas, configuraciones, layout y un PDF válido. Para las pruebas manuales de rendimiento, use CSV de 10, 50, 100, 500 y 1.000 líneas; el progreso indica sopa/página actual y el botón Cancelar deja intacto el destino final.

## Ejecutable de Windows

Después de instalar dependencias, ejecute:

```powershell
.\build_windows.bat
```

El ejecutable aparecerá en `dist\WordSearchBookMaker.exe`. El equivalente manual es:

```powershell
pyinstaller --noconfirm --clean --onefile --windowed --name WordSearchBookMaker main.py
```

## Solución de problemas

- **`python` abre Microsoft Store o no existe:** instale Python 3.12+ desde python.org y compruebe `py -3.12 --version`.
- **CSV no cargado:** guárdelo como UTF-8 y revise comas sobrantes, duplicados y líneas en blanco.
- **No se puede colocar una sopa:** aumente filas/columnas, permita cruces o active más direcciones.
- **No cabe el diseño:** reduzca márgenes, título/lista, o active el ajuste automático.
- **No se abre la ventana:** confirme que el entorno virtual está activo y que `customtkinter` se instaló desde `requirements.txt`.
