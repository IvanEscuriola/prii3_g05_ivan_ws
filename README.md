# Proyecto PRII 3 — Robots Inteligentes

Workspace personal de ROS 2 para la asignatura Proyecto RII 3:
Robots Inteligentes, grupo 05.

Contiene el trabajo del Sprint 1, las actividades preparatorias con
TurtleBot3, Gazebo y LIDAR, y el desarrollo progresivo del Sprint 2.

Cada apartado indica sus instrucciones de ejecución y su estado.

## Autor

Ivan — Grupo 05

## Entorno utilizado

- Ubuntu 24.04 LTS.
- ROS 2 Jazzy Jalisco.
- Python 3.
- Shell: zsh.
- Gazebo Sim.

> El enunciado del Sprint 1 especifica Ubuntu 22.04 y ROS 2 Humble.
> Este proyecto se ha desarrollado y probado con ROS 2 Jazzy.

## 1. Descargar el workspace

```zsh
cd ~/Documents
git clone https://github.com/IvanEscuriola/prii3_g05_ivan_ws.git proy3
cd proy3
```

Si ya existe una carpeta llamada `proy3`, utiliza otro nombre al clonar
y adapta las rutas de los comandos siguientes.

## 2. Dependencias

Se requiere una instalación funcional de ROS 2 Jazzy.

Instalar las herramientas y paquetes utilizados:

```zsh
sudo apt update
sudo apt install \
  git \
  tree \
  python3-colcon-common-extensions \
  python3-rosdep \
  ros-jazzy-turtlesim \
  ros-jazzy-turtlebot3 \
  ros-jazzy-turtlebot3-gazebo \
  ros-jazzy-turtlebot3-teleop \
  ros-jazzy-rviz2 \
  ros-jazzy-rqt-publisher \
  ros-jazzy-rqt-reconfigure
```

Cargar ROS 2:

```zsh
source /opt/ros/jazzy/setup.zsh
```

Con `rosdep` ya inicializado, resolver las dependencias del workspace:

```zsh
cd ~/Documents/proy3
rosdep update
rosdep install --from-paths src --ignore-src -r -y --rosdistro jazzy
```

Si `rosdep` indica que todavía no está inicializado, ejecutar una sola vez:

```zsh
sudo rosdep init
```

Después, repetir `rosdep update` y `rosdep install`.

## 3. Compilar

Desde la raíz del workspace:

```zsh
cd ~/Documents/proy3
source /opt/ros/jazzy/setup.zsh

colcon build --symlink-install

source install/setup.zsh
```

En cada terminal nueva utilizada para ejecutar los paquetes:

```zsh
source /opt/ros/jazzy/setup.zsh
source ~/Documents/proy3/install/setup.zsh
```

## 4. Organización del código

```text
src/
├── g05_prii3_turtlesim/
│   ├── launch/
│   │   └── dibujar_cero.launch.py
│   └── g05_prii3_turtlesim/
│       └── dibujar_0.py
│
└── g05_prii3_move_turtlebot/
    ├── launch/
    │   ├── draw_number.launch.py
    │   └── evitar_colision.launch.py
    ├── models/
    │   └── cubo.sdf
    └── g05_prii3_move_turtlebot/
        ├── draw_number.py
        ├── laser_filter.py
        └── evitar_colision.py
```

Se muestran únicamente los archivos principales.
Cada paquete incluye también `package.xml`, `setup.py` y los demás
archivos necesarios para su instalación.

Para consultar la estructura completa:

```zsh
tree src
```

## 5. Sprint 1 — Dibujo del 0 con turtlesim

### Ejecución

```zsh
ros2 launch g05_prii3_turtlesim dibujar_cero.launch.py
```

El launch inicia turtlesim y el nodo que dibuja el 0 mediante una
secuencia de avances y giros controlados por tiempo.

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

El reinicio utiliza el servicio de reset de turtlesim para limpiar
la ventana y comenzar nuevamente desde su posición inicial.

## 6. Actividades preparatorias del Sprint 2 — TurtleBot3 y Gazebo

Ejercicios de preparación completados y probados en simulación.
Sirven como base para el Sprint 2, pero no cubren por sí solos
todos sus requisitos.

No ejecutar simultáneamente los nodos de dibujo, teleoperación y parada
ante obstáculos: todos pueden publicar órdenes en `/cmd_vel`.

Cerrar la simulación anterior con `Ctrl+C` antes de iniciar otra.

### 6.1. Trayectoria autónoma del 0

```zsh
ros2 launch g05_prii3_move_turtlebot draw_number.launch.py
```

El launch inicia TurtleBot3 Burger en un mundo vacío y el nodo
`draw_number`.

El robot sigue una trayectoria rectangular que representa el 0.
El recorrido se controla mediante velocidades y tiempos, por lo que
su cierre es aproximado.

No se pinta una línea sobre el suelo: se observa el desplazamiento
del robot.

Servicios:

```zsh
# Pausar
ros2 service call /pausar_dibujo std_srvs/srv/SetBool "{data: true}"

# Reanudar
ros2 service call /pausar_dibujo std_srvs/srv/SetBool "{data: false}"

# Reiniciar la secuencia
ros2 service call /reiniciar_dibujo std_srvs/srv/Empty "{}"
```

En esta actividad, reiniciar significa volver al primer movimiento
desde la posición y orientación actuales. No devuelve el robot al
punto de aparición.

Para repetir desde la posición inicial, cerrar y volver a ejecutar
el launch.

### 6.2. Visualización de sensores

Iniciar Waffle en el mundo con obstáculos:

```zsh
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

En otra terminal:

```zsh
ros2 run rviz2 rviz2 --ros-args -p use_sim_time:=true
```

Configurar RViz:

- `Fixed Frame`: `base_footprint`.
- Añadir `TF`.
- Añadir `LaserScan` con el tópico `/scan`.
- Añadir `Image` con el tópico de imagen de la cámara disponible.

Consultar los datos del LIDAR:

```zsh
ros2 topic type /scan
ros2 interface show sensor_msgs/msg/LaserScan
ros2 topic echo /scan --once
```

### 6.3. Filtrado del LIDAR

Con la simulación anterior abierta, ejecutar en otra terminal:

```zsh
ros2 run g05_prii3_move_turtlebot laser_filter
```

El nodo recibe `/scan` y publica el resultado en `/filtered_scan`.

En RViz, añadir un `LaserScan` con `/filtered_scan`.
Desactivar la visualización original para observar únicamente el filtro.

Parámetros:

- `laser_angle`: apertura del sector conservado, en grados,
  centrado en la dirección frontal del sensor.
- `distance`: distancia máxima conservada, en metros.

Ejemplos:

```zsh
ros2 param set /lidar_filter laser_angle 90.0
ros2 param set /lidar_filter distance 2.0
```

Restaurar un sector completo y una distancia de 5 metros:

```zsh
ros2 param set /lidar_filter laser_angle 360.0
ros2 param set /lidar_filter distance 5.0
```

También se pueden modificar desde la interfaz gráfica:

```zsh
ros2 run rqt_reconfigure rqt_reconfigure
```

Seleccionar el nodo `lidar_filter`.

El filtro no modifica `/scan` ni controla el movimiento del robot.

### 6.4. Parada ante obstáculos

Cerrar la simulación anterior e iniciar:

```zsh
ros2 launch g05_prii3_move_turtlebot evitar_colision.launch.py
```

Este launch:

1. Inicia Waffle en un mundo vacío.
2. Ejecuta el nodo `evitar_colision`.
3. Solicita la creación del cubo a los 5 segundos.
4. Solicita su eliminación a los 30 segundos.

El nodo utiliza directamente `/scan`:

- Comprueba un sector frontal de 60 grados.
- Avanza a 0,1 m/s cuando el camino está libre.
- Se detiene si la distancia frontal es de 0,6 m o menos.
- Se detiene si no dispone de medidas utilizables o recientes.
- Continúa cuando desaparece el obstáculo.

La creación y eliminación del cubo utilizan los servicios de Gazebo:

```text
/world/default/create
/world/default/remove
```

Esta configuración presupone un mundo llamado `default` y un robot
que aparece cerca del origen orientado hacia el eje X positivo.

Los tiempos del launch son tiempos reales del ordenador.
Si la simulación tarda en arrancar o funciona lentamente, puede ser
necesario aumentar los tiempos de creación o eliminación.

Al terminar, cerrar el launch con `Ctrl+C`, ya que el robot continúa
avanzando mientras el camino esté libre.

Esta actividad es una demostración en simulación, no un sistema
de seguridad certificado para un robot real.

## 7. Tópicos principales

| Tópico | Tipo | Función |
|---|---|---|
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | Movimiento en turtlesim |
| `/cmd_vel` | `geometry_msgs/msg/TwistStamped` | Movimiento de TurtleBot3 en la configuración utilizada |
| `/scan` | `sensor_msgs/msg/LaserScan` | Lecturas originales del LIDAR |
| `/filtered_scan` | `sensor_msgs/msg/LaserScan` | Lecturas filtradas |

## 8. Comandos de comprobación

```zsh
ros2 node list
ros2 topic list
ros2 service list
ros2 topic info /cmd_vel -v
```

## 9. Control de versiones

La rama principal es `main`.

Las carpetas `build/`, `install/` y `log/` no se incluyen en Git,
porque se generan al compilar.

Consultar el estado y el historial:

```zsh
git status
git log --oneline
```
