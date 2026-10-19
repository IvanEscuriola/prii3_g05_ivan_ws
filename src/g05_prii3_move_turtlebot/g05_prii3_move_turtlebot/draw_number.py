import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from std_srvs.srv import SetBool, Empty


class DrawNumber(Node):
    def __init__(self):
        super().__init__('draw_number')

        self.publicador = self.create_publisher(
            TwistStamped, '/cmd_vel', 10
        )

        self.create_service(
            SetBool, '/pausar_dibujo', self.pausar
        )

        self.create_service(
            Empty, '/reiniciar_dibujo', self.reiniciar
        )

        # Velocidad lineal, velocidad angular, intervalos de 0,1 s.
        self.movimientos = [
            (0.1, 0.0, 100),   # Avanzar 1 metro
            (0.0, 0.5, 31),    # Girar aproximadamente 90 grados
            (0.1, 0.0, 150),   # Avanzar 1,5 metros
            (0.0, 0.5, 31),
            (0.1, 0.0, 100),
            (0.0, 0.5, 31),
            (0.1, 0.0, 150),
        ]

        self.paso = 0
        self.contador = 0
        self.pausado = False

        self.create_timer(0.1, self.actualizar)

        self.get_logger().info('Nodo draw_number iniciado')

    def enviar_velocidad(self, lineal, angular):
        mensaje = TwistStamped()

        mensaje.header.stamp = self.get_clock().now().to_msg()
        mensaje.twist.linear.x = lineal
        mensaje.twist.angular.z = angular

        self.publicador.publish(mensaje)

    def actualizar(self):
        # Esperar a que el simulador esté conectado al publicador.
        if self.publicador.get_subscription_count() == 0:
            return

        if self.pausado or self.paso >= len(self.movimientos):
            self.enviar_velocidad(0.0, 0.0)
            return

        lineal, angular, duracion = self.movimientos[self.paso]

        self.enviar_velocidad(lineal, angular)
        self.contador += 1

        if self.contador >= duracion:
            self.contador = 0
            self.paso += 1

            if self.paso == len(self.movimientos):
                self.get_logger().info('Trayectoria terminada')

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
            'Trayectoria reiniciada desde la posicion actual'
        )

        return respuesta


def main(args=None):
    rclpy.init(args=args)
    nodo = DrawNumber()

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
