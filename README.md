# Proyecto PRII 3 — Robots Inteligentes

Workspace personal de ROS 2 para la asignatura Proyecto RII 3,
grupo 05.

Incluye el trabajo de Sprint 1, las actividades preparatorias
con TurtleBot3, Gazebo y LIDAR, y los comportamientos de simulación
desarrollados para Sprint 2.

## Estado actual

- Sprint 1: dibujo del `0` en turtlesim.
- Simulación TurtleBot3: movimiento autónomo, parada ante obstáculos
  y esquiva de la caja de prueba.
- Visión ArUco: detector experimental ejecutado desde el portátil.
- Jetbot: pendiente de desarrollar y probar con el robot real.
- Calibración y demostración de cámara/ArUco del equipo: consultar
  el material preparado por el compañero responsable.

## Entorno utilizado

- Ubuntu 24.04 LTS.
- ROS 2 Jazzy Jalisco.
- Python 3.
- Shell: zsh.
- Gazebo Sim para las pruebas de TurtleBot3.

> El enunciado del Sprint 1 indica Ubuntu 22.04 y ROS 2 Humble.
> Este workspace se ha desarrollado y probado en Ubuntu 24.04
> con ROS 2 Jazzy.

## Descargar el workspace

```zsh
cd ~/Documents
git clone https://github.com/IvanEscuriola/prii3_g05_ivan_ws.git proy3
cd proy3
```

Si ya tienes una carpeta `proy3`, clona el repositorio con otro nombre
y adapta las rutas siguientes.

## Dependencias

Se requiere una instalación funcional de ROS 2 Jazzy.

```zsh
sudo apt update
sudo apt install \
  git \
  tree \
  python3-colcon-common-extensions \
  python3-rosdep \
  python3-opencv \
  ros-jazzy-turtlesim \
  ros-jazzy-turtlebot3 \
  ros-jazzy-turtlebot3-gazebo \
  ros-jazzy-turtlebot3-teleop \
  ros-jazzy-rviz2 \
  ros-jazzy-rqt-publisher \
  ros-jazzy-rqt-reconfigure
```

Cargar ROS 2 en cada terminal zsh:

```zsh
source /opt/ros/jazzy/setup.zsh
```

Resolver las dependencias ROS del workspace:

```zsh
cd ~/Documents/proy3
rosdep update
rosdep install --from-paths src --ignore-src -r -y --rosdistro jazzy
```

Si `rosdep` todavía no está inicializado:

```zsh
sudo rosdep init
rosdep update
```

## Compilar el workspace

```zsh
cd ~/Documents/proy3
source /opt/ros/jazzy/setup.zsh
colcon build --symlink-install
source install/setup.zsh
```

En cada terminal nueva desde la que vayas a ejecutar paquetes:

```zsh
source /opt/ros/jazzy/setup.zsh
source ~/Documents/proy3/install/setup.zsh
```

## Organización del código

```text
src/
├── g05_prii3_turtlesim/
│   ├── launch/
│   │   └── dibujar_cero.launch.py
│   └── g05_prii3_turtlesim/
│       └── dibujar_0.py
│
├── g05_prii3_move_turtlebot/
│   ├── launch/
│   │   ├── draw_number.launch.py
│   │   ├── evitar_colision.launch.py
│   │   ├── collision_avoidance.launch.py
│   │   └── obstacle_avoidance.launch.py
│   ├── models/
│   │   └── cubo.sdf
│   └── g05_prii3_move_turtlebot/
│       ├── draw_number.py
│       ├── laser_filter.py
│       ├── evitar_colision.py
│       ├── collision_avoidance.py
│       └── obstacle_avoidance.py
│
└── g05_prii3_vision/
    └── g05_prii3_vision/
        └── detectar_aruco.py
```

La estructura muestra los archivos principales; cada paquete incluye
también sus archivos de configuración ROS, como `package.xml`
y `setup.py`.

Para ver la estructura real:

```zsh
tree src
```

## Sprint 1 — Dibujo del 0 en turtlesim

### Ejecutar

```zsh
ros2 launch g05_prii3_turtlesim dibujar_cero.launch.py
```

El nodo mueve la tortuga mediante una secuencia de avances y giros
controlados por tiempo para dibujar el `0`.

### Servicios

Ejecutar desde otra terminal con el entorno cargado.

Pausar:

```zsh
ros2 service call /pausar_reanudar_cero std_srvs/srv/SetBool "{data: true}"
```

Reanudar:

```zsh
ros2 service call /pausar_reanudar_cero std_srvs/srv/SetBool "{data: false}"
```

Reiniciar:

```zsh
ros2 service call /reiniciar_cero std_srvs/srv/Empty "{}"
```

## Actividades preparatorias — TurtleBot3, Gazebo y LIDAR

Estas actividades sirvieron para familiarizarse con los mundos,
el control por velocidad, RViz y los datos del láser.

No ejecutar dos controladores de movimiento al mismo tiempo:
varios nodos publicando en `/cmd_vel` pueden competir por el control.
Cerrar cada simulación con `Ctrl+C` antes de iniciar otra.

### Movimiento autónomo de prueba

```zsh
ros2 launch g05_prii3_move_turtlebot draw_number.launch.py
```

El robot sigue una trayectoria rectangular que representa el `0`.
La trayectoria se controla por tiempos y es aproximada; no se dibuja
una línea en el suelo.

Servicios de este nodo:

```zsh
# Pausar
ros2 service call /pausar_dibujo std_srvs/srv/SetBool "{data: true}"

# Reanudar
ros2 service call /pausar_dibujo std_srvs/srv/SetBool "{data: false}"

# Reiniciar la secuencia desde la posición actual
ros2 service call /reiniciar_dibujo std_srvs/srv/Empty "{}"
```

### Visualizar el LIDAR y TF en RViz

Iniciar el mundo TurtleBot3:

```zsh
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

En otra terminal:

```zsh
ros2 run rviz2 rviz2 --ros-args -p use_sim_time:=true
```

En RViz, establecer `base_footprint` como `Fixed Frame` y añadir
las visualizaciones `TF` y `LaserScan` sobre `/scan`.

Consultar el tipo y los datos del láser:

```zsh
ros2 topic type /scan
ros2 interface show sensor_msgs/msg/LaserScan
ros2 topic echo /scan --once
```

### Filtrar el LIDAR

Con la simulación iniciada:

```zsh
ros2 run g05_prii3_move_turtlebot laser_filter
```

El nodo se suscribe a `/scan` y publica el resultado en
`/filtered_scan`. En RViz, añade una visualización `LaserScan`
para `/filtered_scan`.

Parámetros disponibles:

- `laser_angle`: apertura angular conservada, en grados, centrada
  en la dirección frontal del sensor.
- `distance`: distancia máxima conservada, en metros.

Ejemplo:

```zsh
ros2 param set /lidar_filter laser_angle 90.0
ros2 param set /lidar_filter distance 2.0
```

Restaurar el sector completo y una distancia de 5 m:

```zsh
ros2 param set /lidar_filter laser_angle 360.0
ros2 param set /lidar_filter distance 5.0
```

La interfaz de parámetros puede abrirse con:

```zsh
ros2 run rqt_reconfigure rqt_reconfigure
```

El filtro solo procesa y publica datos del LIDAR; no controla
el movimiento del robot.

## Sprint 2 — Comportamientos TurtleBot3 en simulación

Las siguientes pruebas se han ejecutado en Gazebo con Waffle.
La esquiva está configurada para el cubo y el mundo de la demostración;
no es un planificador general para cualquier obstáculo.

### `draw_number`: trayectoria autónoma

```zsh
ros2 launch g05_prii3_move_turtlebot draw_number.launch.py
```

Inicia TurtleBot3 en un mundo vacío y ejecuta la trayectoria del `0`.
Usa mensajes `geometry_msgs/msg/TwistStamped` en `/cmd_vel`.

Los servicios de pausa, reanudación y reinicio se muestran en
«Movimiento autónomo de prueba».

### `collision_avoidance`: parar y continuar

```zsh
ros2 launch g05_prii3_move_turtlebot collision_avoidance.launch.py
```

El nodo combina la trayectoria con la lectura del LIDAR. Se detiene
si detecta un obstáculo en el sector frontal y continúa el movimiento
cuando el camino vuelve a estar libre.

El launch añade y retira automáticamente el cubo de prueba. Para repetir
la demostración desde el inicio, cerrar el launch con `Ctrl+C` y
ejecutarlo de nuevo. El servicio de reinicio de la secuencia no vuelve
a lanzar el proceso ni recrea el cubo.

### `obstacle_avoidance`: rodear el cubo

```zsh
ros2 launch g05_prii3_move_turtlebot obstacle_avoidance.launch.py
```

El nodo utiliza `/scan` para detectar el cubo y `/odom` para obtener
la posición estimada del robot. En la demostración se desvía por el
lado izquierdo y recupera el recorrido del `0`.

La maniobra está preparada para la caja y las coordenadas de este
escenario. No debe interpretarse como una solución general para
entornos desconocidos ni como un sistema de seguridad para un robot real.

### Tópicos de TurtleBot3

| Tópico | Tipo | Función |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/TwistStamped` | Comandos de velocidad en esta instalación |
| `/scan` | `sensor_msgs/msg/LaserScan` | Lecturas originales del LIDAR |
| `/filtered_scan` | `sensor_msgs/msg/LaserScan` | Lecturas procesadas por `laser_filter` |
| `/odom` | `nav_msgs/msg/Odometry` | Posición y velocidad estimadas |

## Visión — prueba personal de detección ArUco

El script experimental detecta marcadores del diccionario
`DICT_4X4_50` y muestra su ID. También dibuja ejes 3D usando
un modelo de cámara aproximado, ya que esta prueba se ejecuta
con la cámara del portátil sin calibrar.

Por tanto, los ejes y la pose no son una medición calibrada
y no sustituyen la demostración del equipo con la cámara del robot.

### Ejecutar el script

Si se utiliza el entorno virtual de visión creado localmente:

```zsh
source ~/Documents/proy3/.venv-vision/bin/activate

python ~/Documents/proy3/src/g05_prii3_vision/g05_prii3_vision/detectar_aruco.py
```

Pulsar `q` en la ventana para salir.

El entorno virtual `.venv-vision` no se incluye en Git. Su configuración
depende del equipo donde se ejecute.

## Robot real Jetbot

Pendiente de implementar y probar. Los tópicos, tipos de mensaje,
velocidades y sensores deberán verificarse con el robot real antes
de reutilizar el código de simulación.

## Comprobaciones ROS útiles

```zsh
ros2 node list
ros2 topic list -t
ros2 service list
ros2 topic info /cmd_vel -v
```

## Git

La rama de entrega es `main`. No se deben versionar las carpetas
generadas por la compilación (`build/`, `install/`, `log/`) ni el
entorno virtual local `.venv-vision/`.

```zsh
git status
git log --oneline
```
