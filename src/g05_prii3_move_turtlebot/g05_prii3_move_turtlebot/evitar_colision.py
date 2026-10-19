import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan


class EvitarColision(Node):
    def __init__(self):
        super().__init__('evitar_colision')

        self.publicador = self.create_publisher(
            TwistStamped, '/cmd_vel', 10
        )

        self.create_subscription(
            LaserScan,
            '/scan',
            self.leer_laser,
            qos_profile_sensor_data
        )

        self.distancia_frontal = 0.0
        self.ultima_lectura = None

        self.create_timer(0.1, self.mover)

        self.get_logger().info('Nodo de parada ante obstaculos iniciado')

    def leer_laser(self, mensaje):
        distancias = []

        for i in range(len(mensaje.ranges)):
            angulo = mensaje.angle_min + i * mensaje.angle_increment

            # Normalizar el ángulo entre -180 y 180 grados.
            angulo = math.degrees(
                math.atan2(math.sin(angulo), math.cos(angulo))
            )

            # Mirar únicamente un sector frontal de 60 grados.
            if abs(angulo) <= 30:
                distancia = mensaje.ranges[i]

                if math.isfinite(distancia):
                    if mensaje.range_min <= distancia <= mensaje.range_max:
                        distancias.append(distancia)

                elif distancia == float('inf'):
                    # Sin obstáculo detectado dentro del alcance.
                    distancias.append(mensaje.range_max)

        if distancias:
            self.distancia_frontal = min(distancias)
        else:
            # Sin medidas utilizables, no avanzamos.
            self.distancia_frontal = 0.0

        self.ultima_lectura = self.get_clock().now()

    def mover(self):
        velocidad = TwistStamped()
        velocidad.header.stamp = self.get_clock().now().to_msg()

        if self.ultima_lectura is not None:
            tiempo_sin_datos = (
                self.get_clock().now() - self.ultima_lectura
            ).nanoseconds / 1e9

            if tiempo_sin_datos < 1.0 and self.distancia_frontal > 0.6:
                velocidad.twist.linear.x = 0.1

        self.publicador.publish(velocidad)


def main(args=None):
    rclpy.init(args=args)
    nodo = EvitarColision()

    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            parada = TwistStamped()
            parada.header.stamp = nodo.get_clock().now().to_msg()
            nodo.publicador.publish(parada)

        nodo.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
