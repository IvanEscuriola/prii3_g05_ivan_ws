import cv2
import numpy as np


def main():
    diccionario = cv2.aruco.getPredefinedDictionary(
        cv2.aruco.DICT_4X4_50
    )

    detector = cv2.aruco.ArucoDetector(diccionario)

    # Lado del cuadrado negro exterior, sin el margen blanco.
    # 0.05 significa 5 centímetros. Ajustarlo al marcador utilizado.
    lado = 0.05

    # Coordenadas de las cuatro esquinas del marcador en 3D.
    puntos_3d = np.array([
        [-lado / 2,  lado / 2, 0],
        [ lado / 2,  lado / 2, 0],
        [ lado / 2, -lado / 2, 0],
        [-lado / 2, -lado / 2, 0],
    ], dtype=np.float32)

    camara = cv2.VideoCapture(0)

    if not camara.isOpened():
        print('No se ha podido abrir la camara')
        return

    print('Pulsa q en la ventana para salir')
    print('AVISO: pose aproximada, camara sin calibrar')

    try:
        while True:
            correcto, imagen = camara.read()

            if not correcto:
                print('No se ha podido leer la imagen')
                break

            alto, ancho = imagen.shape[:2]

            # Modelo aproximado: NO son parámetros calibrados.
            focal = float(ancho)

            matriz_camara = np.array([
                [focal, 0, ancho / 2],
                [0, focal, alto / 2],
                [0, 0, 1],
            ], dtype=np.float64)

            distorsion = np.zeros((5, 1), dtype=np.float64)

            gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

            esquinas, ids, descartados = detector.detectMarkers(gris)

            if ids is not None:
                cv2.aruco.drawDetectedMarkers(imagen, esquinas, ids)

                for esquina in esquinas:
                    puntos_2d = esquina.reshape(4, 2)

                    encontrada, rotacion, traslacion = cv2.solvePnP(
                        puntos_3d,
                        puntos_2d,
                        matriz_camara,
                        distorsion,
                        flags=cv2.SOLVEPNP_IPPE_SQUARE
                    )

                    if encontrada:
                        cv2.drawFrameAxes(
                            imagen,
                            matriz_camara,
                            distorsion,
                            rotacion,
                            traslacion,
                            lado / 2
                        )

                texto = 'IDs: ' + ', '.join(
                    str(numero) for numero in ids.flatten()
                )
            else:
                texto = 'Sin marcadores detectados'

            cv2.putText(
                imagen, texto, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 255, 0), 2
            )

            cv2.putText(
                imagen, 'POSE APROXIMADA - SIN CALIBRAR', (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 165, 255), 1
            )

            cv2.imshow('ArUco: ID y ejes 3D', imagen)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        camara.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
