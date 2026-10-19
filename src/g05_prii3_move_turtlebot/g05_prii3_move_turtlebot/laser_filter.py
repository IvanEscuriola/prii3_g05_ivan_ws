import copy
import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class LaserFilter(Node):
    def __init__(self):
        super().__init__('lidar_filter')

        self.declare_parameter('laser_angle', 360.0)
        self.declare_parameter('distance', 5.0)

        self.create_subscription(
            LaserScan,
            '/scan',
            self.filtrar,
            qos_profile_sensor_data
        )

        self.publicador = self.create_publisher(
            LaserScan, '/filtered_scan', 10
        )

        self.get_logger().info('Filtro del LIDAR iniciado')

    def filtrar(self, mensaje):
        angulo = self.get_parameter('laser_angle').value
        distancia = self.get_parameter('distance').value

        filtrado = copy.deepcopy(mensaje)

        for i in range(len(mensaje.ranges)):
            # Calcular la dirección de esta medida.
            direccion = (
                mensaje.angle_min + i * mensaje.angle_increment
            )

            # Expresar el ángulo entre -180 y 180 grados.
            direccion = math.degrees(
                math.atan2(math.sin(direccion), math.cos(direccion))
            )

            fuera_del_angulo = abs(direccion) > angulo / 2
            fuera_de_distancia = mensaje.ranges[i] > distancia

            if fuera_del_angulo or fuera_de_distancia:
                filtrado.ranges[i] = float('inf')

        self.publicador.publish(filtrado)


def main(args=None):
    rclpy.init(args=args)
    nodo = LaserFilter()

    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
