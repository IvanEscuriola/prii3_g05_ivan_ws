import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan


class ObstacleAvoidance(Node):
    def __init__(self):
        super().__init__('obstacle_avoidance')

        self.publicador = self.create_publisher(
            TwistStamped, '/cmd_vel', 10
        )

        self.create_subscription(
            Odometry, '/odom', self.leer_odom, qos_profile_sensor_data
        )

        self.create_subscription(
            LaserScan, '/scan', self.leer_laser, qos_profile_sensor_data
        )

        # Objetivos del 0 en el sistema de coordenadas odom.
        self.recorrido = [
            (2.8, 0.0),
            (2.8, 2.0),
            (0.0, 2.0),
            (0.0, 0.0),
        ]

        self.indice = 0
        self.desvio = []
        self.esquiva_realizada = False

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.distancia_frontal = 0.0

        self.ultima_odom = None
        self.ultimo_scan = None

        self.create_timer(0.1, self.actualizar)

        self.get_logger().info('Obstacle avoidance iniciado')

    def leer_odom(self, mensaje):
        self.x = mensaje.pose.pose.position.x
        self.y = mensaje.pose.pose.position.y

        q = mensaje.pose.pose.orientation

        self.yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        )

        self.ultima_odom = self.get_clock().now()

    def leer_laser(self, mensaje):
        distancias = []

        for i, distancia in enumerate(mensaje.ranges):
            angulo = mensaje.angle_min + i * mensaje.angle_increment
            angulo = math.atan2(math.sin(angulo), math.cos(angulo))

            if abs(angulo) <= math.radians(30):
                if math.isfinite(distancia):
                    if mensaje.range_min <= distancia <= mensaje.range_max:
                        distancias.append(distancia)

                elif distancia == float('inf'):
                    distancias.append(mensaje.range_max)

        self.distancia_frontal = min(distancias) if distancias else 0.0
        self.ultimo_scan = self.get_clock().now()

    def enviar(self, lineal, angular):
        mensaje = TwistStamped()
        mensaje.header.stamp = self.get_clock().now().to_msg()
        mensaje.twist.linear.x = lineal
        mensaje.twist.angular.z = angular
        self.publicador.publish(mensaje)

    def datos_recientes(self):
        if self.ultima_odom is None or self.ultimo_scan is None:
            return False

        ahora = self.get_clock().now()

        edad_odom = (ahora - self.ultima_odom).nanoseconds / 1e9
        edad_scan = (ahora - self.ultimo_scan).nanoseconds / 1e9

        return edad_odom < 1.0 and edad_scan < 1.0

    def ir_a(self, objetivo):
        dx = objetivo[0] - self.x
        dy = objetivo[1] - self.y

        if math.hypot(dx, dy) < 0.12:
            return True

        direccion = math.atan2(dy, dx)
        error = math.atan2(
            math.sin(direccion - self.yaw),
            math.cos(direccion - self.yaw)
        )

        # Reducir el avance cuando hace falta girar mucho.
        lineal = 0.12 if abs(error) < 0.35 else 0.04
        angular = max(-0.8, min(0.8, 1.5 * error))

        self.enviar(lineal, angular)
        return False

    def actualizar(self):
        if not self.datos_recientes():
            self.enviar(0.0, 0.0)
            return

        if self.indice >= len(self.recorrido):
            self.enviar(0.0, 0.0)
            return

        # Parada preventiva si algo está demasiado cerca.
        if self.distancia_frontal < 0.35:
            self.enviar(0.0, 0.0)
            return

        # Primera prueba: una caja en el primer lado del 0.
        if (
            self.indice == 0
            and not self.esquiva_realizada
            and self.distancia_frontal < 0.95
        ):
            self.desvio = [
                (self.x + 0.15, 1.0),
                (2.25, 1.0),
                (2.25, 0.0),
            ]

            self.esquiva_realizada = True
            self.get_logger().info('Obstaculo: iniciando desvio izquierdo')

        if self.desvio:
            if self.ir_a(self.desvio[0]):
                self.desvio.pop(0)

                if not self.desvio:
                    self.get_logger().info('Desvio terminado')
            return

        if self.ir_a(self.recorrido[self.indice]):
            self.indice += 1

            if self.indice == len(self.recorrido):
                self.enviar(0.0, 0.0)
                self.get_logger().info('Recorrido terminado')


def main(args=None):
    rclpy.init(args=args)
    nodo = ObstacleAvoidance()

    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            nodo.enviar(0.0, 0.0)

        nodo.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

