# Ashen Oath

Ashen Oath es una aventura de mazmorras por turnos, contada con texto y color. Kael explora rutas, se enfrenta a criaturas y jefes, encuentra objetos y aprende a sobrevivir usando acero y magia.

## Requisitos

- Python 3.10 o posterior.
- Tkinter para la interfaz gráfica.
- Pygame para reproducir música. La aventura puede abrir sin Pygame, pero no tendrá audio.

## Ubuntu y Debian

Instalá Tkinter y el soporte para entornos virtuales con el gestor de paquetes de tu sistema:

```bash
sudo apt install python3-tk python3-venv
```

Desde la carpeta descargada del proyecto, creá un entorno aislado e instalá las dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

## Windows

Instalá Python 3 desde [python.org](https://www.python.org/downloads/) y asegurate de incluir Tcl/Tk (normalmente viene con el instalador oficial). Abrí PowerShell en la carpeta del proyecto y ejecutá:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Si PowerShell impide activar el entorno, podés ejecutar el intérprete directamente: `.venv\Scripts\python.exe main.py`.

## macOS

Instalá Python 3, abrí Terminal en la carpeta del proyecto y ejecutá:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Si Tkinter no está disponible en tu instalación de Python, instalá una distribución que lo incluya y volvé a intentar.

## Controles

Durante el combate, usá los botones para atacar, defenderte, lanzar hechizos o gastar un botiquín. Leé la intención del enemigo antes de elegir. La mochila, el equipo y las estadísticas están en el panel lateral desplazable.

La música puede silenciarse desde el botón superior. En el menú principal, **Invitame un café** abre la página de apoyo de Ko-fi en el navegador.

## Archivos de audio e imagen

El juego busca la música en `Audio/` y el emblema en `assets/`. Consultá [ASSETS.md](ASSETS.md) para conocer el alcance de la licencia de esos recursos.

## Licencia

El código fuente se distribuye bajo la licencia MIT. La música y el emblema tienen condiciones independientes; la licencia MIT del código no concede derechos adicionales sobre esos archivos. Ver [LICENSE](LICENSE) y [ASSETS.md](ASSETS.md).
