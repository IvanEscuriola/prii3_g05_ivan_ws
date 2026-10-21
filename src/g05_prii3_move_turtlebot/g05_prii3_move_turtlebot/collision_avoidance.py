import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan
from std_srvs.srv import SetBool, Empty


class CollisionAvoidance(Node):
    def __init__(self):
        super().__init__('collision_avoidance')

        self.publicador = self.create_publisher(
            TwistStamped, '/cmd_vel', 10
        )

        self.create_subscription(
            LaserScan,
            '/scan',
            self.leer_laser,
            qos_profile_sensor_data
        )

        self.create_service(
            SetBool, '/pausar_dibujo', self.pausar
        )

        self.create_service(
            Empty, '/reiniciar_dibujo', self.reiniciar
        )

        # Velocidad lineal, velocidad angular, intervalos de 0,1 s.
        self.movimientos = [
            (0.1, 0.0, 100),
            (0.0, 0.5, 31),
            (0.1, 0.0, 150),
            (0.0, 0.5, 31),
            (0.1, 0.0, 100),
            (0.0, 0.5, 31),
            (0.1, 0.0, 150),
        ]

        self.paso = 0
        self.contador = 0
        self.pausado = False

        self.distancia_frontal = 0.0
        self.ultima_lectura = None

        self.create_timer(0.1, self.actualizar)

        self.get_logger().info('Collision avoidance iniciado')

    def enviar_velocidad(self, lineal, angular):
        mensaje = TwistStamped()
        mensaje.header.stamp = self.get_clock().now().to_msg()
        mensaje.twist.linear.x = lineal
        mensaje.twist.angular.z = angular

        self.publicador.publish(mensaje)

    def leer_laser(self, mensaje):
        distancias = []

        for i in range(len(mensaje.ranges)):
            angulo = mensaje.angle_min + i * mensaje.angle_increment

            angulo = math.degrees(
                math.atan2(math.sin(angulo), math.cos(angulo))
            )

            # Sector frontal: de -30 a +30 grados.
            if abs(angulo) <= 30:
                distancia = mensaje.ranges[i]

                if math.isfinite(distancia):
                    if mensaje.range_min <= distancia <= mensaje.range_max:
                        distancias.append(distancia)

                elif distancia == float('inf'):
                    distancias.append(mensaje.range_max)

        if distancias:
            self.distancia_frontal = min(distancias)
        else:
            self.distancia_frontal = 0.0

        self.ultima_lectura = self.get_clock().now()

    def actualizar(self):
        if self.pausado or self.paso >= len(self.movimientos):
            self.enviar_velocidad(0.0, 0.0)
            return

        # No mover el robot hasta recibir datos del láser.
        if self.ultima_lectura is None:
            self.enviar_velocidad(0.0, 0.0)
            return

        tiempo_sin_datos = (
            self.get_clock().now() - self.ultima_lectura
        ).nanoseconds / 1e9

        # Si faltan datos recientes o hay un obstáculo, detenerse.
        if tiempo_sin_datos >= 1.0 or self.distancia_frontal <= 0.6:
            self.enviar_velocidad(0.0, 0.0)
            return

        lineal, angular, duracion = self.movimientos[self.paso]

        self.enviar_velocidad(lineal, angular)
        self.contador += 1

        if self.contador >= duracion:
            self.contador = 0
            self.paso += 1

            if self.paso == len(self.movimientos):
                self.get_logger().info('Dibujo terminado')

    def pausar(self, solicitud, respuesta):
        self.pausado = solicitud.data
        self.enviar_velocidad(0.0, 0.0)

        respuesta.success = True
        respuesta.message = (
            'Dibujo pausado' if self.pausado
            else 'Dibujo reanudado'
        )

        return respuesta

    def reiniciar(self, solicitud, respuesta):
        self.enviar_velocidad(0.0, 0.0)

        self.paso = 0
        self.contador = 0
        self.pausado = False

        self.get_logger().info(
            'Secuencia reiniciada desde la posicion actual'
        )

        return respuesta


def main(args=None):
    rclpy.init(args=args)
    nodo = CollisionAvoidance()

    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            nodo.enviar_velocidad(0.0, 0.0)

        nodo.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
