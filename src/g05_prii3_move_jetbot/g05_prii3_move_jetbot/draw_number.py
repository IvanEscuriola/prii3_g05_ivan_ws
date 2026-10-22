import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import SetBool, Empty


class DrawNumber(Node):
    def __init__(self):
        super().__init__('draw_number_jetbot')

        self.publicador = self.create_publisher(
            Twist, '/cmd_vel', 10
        )

        self.create_service(
            SetBool, '/jetbot/pausar_dibujo', self.pausar
        )

        self.create_service(
            Empty, '/jetbot/reiniciar_dibujo', self.reiniciar
        )

        # Velocidad lineal, angular e intervalos de 0,1 segundos.
        # Recorrido nominal: 0,4 x 0,6 metros.
        self.movimientos = [
            (0.05, 0.0, 80),
            (0.0, 0.3, 52),
            (0.05, 0.0, 120),
            (0.0, 0.3, 52),
            (0.05, 0.0, 80),
            (0.0, 0.3, 52),
            (0.05, 0.0, 120),
        ]

        self.paso = 0
        self.contador = 0

        # Nunca empezar a moverse automáticamente.
        self.pausado = True

        self.create_timer(0.1, self.actualizar)

        self.get_logger().info(
            'Preparado y PAUSADO. Reanudar mediante servicio.'
        )

    def enviar_velocidad(self, lineal, angular):
        mensaje = Twist()
        mensaje.linear.x = lineal
        mensaje.angular.z = angular
        self.publicador.publish(mensaje)

    def actualizar(self):
        if self.pausado or self.paso >= len(self.movimientos):
            self.enviar_velocidad(0.0, 0.0)
            return

        if self.publicador.get_subscription_count() == 0:
            self.pausado = True
            self.get_logger().error(
                'Sin suscriptor de velocidad. Se requiere reanudacion.'
            )
            return

        lineal, angular, duracion = self.movimientos[self.paso]

        self.enviar_velocidad(lineal, angular)
        self.contador += 1

        if self.contador >= duracion:
            self.contador = 0
            self.paso += 1

            if self.paso == len(self.movimientos):
                self.enviar_velocidad(0.0, 0.0)
                self.pausado = True
                self.get_logger().info('Dibujo terminado')

    def pausar(self, solicitud, respuesta):
        self.enviar_velocidad(0.0, 0.0)

        if (
            not solicitud.data
            and self.publicador.get_subscription_count() == 0
        ):
            respuesta.success = False
            respuesta.message = 'No hay controlador conectado'
            return respuesta

        self.pausado = solicitud.data

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
        self.pausado = True

        self.get_logger().info(
            'Secuencia reiniciada y pausada desde la posicion actual'
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

