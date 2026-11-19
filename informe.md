# Fragmentación

integrante:
- Benjamín Álvarez
- Vicente Garrido

Repositorio: https://github.com/bergamen/Fragmentacion.git

## Estructura del Header IP

Para soportar la fragmentación y el re-ensamblado en `parse_packet` y `create_packet`, se extendió el header IP a un tamaño fijo de **16 bytes** con la siguiente distribución de campos:

- **Dirección IP (4 bytes):** 1 byte por cada octeto de la dirección IPv4 de destino.
- **Puerto (2 bytes):** Entero sin signo que indica el puerto de destino.
- **TTL (1 byte):** Tiempo de vida del paquete o fragmento.
- **ID (2 bytes):** Identificador numérico compartido por todos los fragmentos pertenecientes a un mismo datagrama IP.
- **Offset (2 bytes):** Posición de inicio (en bytes) de los datos del fragmento respecto al mensaje del datagrama original.
- **Tamaño (4 bytes):** Largo en bytes del mensaje contenido en el paquete o fragmento actual (sin contar los 16 bytes del header).
- **FLAG (1 byte):** Toma el valor `1` si quedan más fragmentos después del actual y `0` si es el último fragmento o un paquete sin fragmentar.

## Lectura de MTU y Forwarding

Para que los routers consideren el MTU de cada enlace, se modificó la función `check_routes` para que además de buscar la ruta que corresponde a la dirección de destino, lea también el último valor de la línea en la tabla de rutas y lo guarde como entero. Con esto la función ahora retorna tanto la dirección del siguiente salto como su MTU (`re_address, mtu`). Luego, cuando un paquete llega a un router y no es para él, primero se le resta 1 a su `TTL`, después se pasa por `fragment_IP_packet` usando el MTU que nos dio `check_routes`, y por último se recorre la lista de fragmentos resultante enviando cada uno hacia la siguiente dirección.

## Implementación de fragmentación

Para esto, primero revisa si el tamaño de los headers con el mensaje sean igual o menores al MTU, con esto es capaz de ver si es posible de mandarlo completo, sino, toma la máxima porsión del mensaje y la separa. Con esta porsión se setea que su flag es 1, mientras que la otra porsión se setea un offset sumando el tamaño de la primera porsion a su offset, con esto nos aseguramos que si es un mensaje ya fragmentado, pueda mantener su posicion. Luego la primera parte se pone en un arreglo unico y se concatena con el resultado de aplicarle la funcion de fragmentacion a la segunda parte

## Implementación de Re-Emsamblado

Se setea una base de Paquete con la informacion que no cambia del mensaje original, y se setea su flag en 1 y el mensaje como vacio. Luego entra en un bucle usando un contador revisando cada segmento en el arreglo, si el tamaño del mensaje ya guardado es igual al offset, este se agrega al paquete base y se setea su flag como la flag de ese mensaje, de modo que si este era 0, significa que el mensaje termino, y vuelve la cuenta a 0. Si no encontro ningun mensaje que correspondiera al offset, se sale del bucle al superar el largo del arreglo y devuelve 0. Con eso se uso que un mensaje sin fragmentar tiene que tener su flag igual a 0.

## Desicion de diseño

Para manejar la recepción en el router de destino, se implementó un diccionario que usa el `ID` del paquete como llave y guarda en una lista todos los fragmentos que van llegando asociados a ese `ID`. Cada vez que el router recibe un fragmento dirigido a sí mismo, lo agrega a la lista correspondiente e intenta armar el paquete llamando a `reassemble_IP_packet`; si aún faltan fragmentos retorna `None` y sigue esperando, pero cuando logra armarlo completo imprime el mensaje en pantalla y elimina ese `ID` del diccionario para que no se mezclen los fragmentos si más adelante se envía otro paquete con el mismo `ID`.

Para el ensamblado, se tomo la desicion de que se guardara tambien el tamaño del mensaje asociado al id, con el fin de que solo cuando sepa que llego el mensaje completo intentara re-emsamblarlo. Esto debido a que al hacer pruebas, algunos paquetes se perdian, de modo que se considero que al tratar armar los paquetes de nuevo, el timpo usado para este pudo haber hecho que ignorara los mensajes en ese tiempo. Esto fue una suposicion, pero funciono al aplicarlo.

## Pruebas

En primer lugar, se comprobó el manejo del `TTL` y la alternancia de rutas mediante *Round-Robin* enviando un paquete pequeño desde `R1` hacia `R5` con `mensaje="hola!"` (`Tamaño=5`, `TTL=10`, `ID=347`, `Offset=0`, `FLAG=0`). Dado que el tamaño total del datagrama es de 21 bytes, el cual es menor que el MTU mínimo de la red (50 bytes), el paquete recorrió los enlaces sin sufrir fragmentación, disminuyendo su `TTL` en 1 por cada salto y alternando en `R2` entre los caminos por `R3` y `R4` al enviarlo repetidas veces, llegando e imprimiéndose `"hola!"` directamente en `R5`.

Para la segunda prueba se envió varias veces un paquete de 150 bytes totales (16 bytes de header y 134 bytes de mensaje) desde `R1` hacia `R5`. Al salir de `R1` a `R2` (`MTU = 100`), el paquete se divide en 2 fragmentos (uno de 100 bytes y otro de 66 bytes), y al llegar a `R2` el *Round-Robin* los reparte hacia `R3` (`MTU = 50`) y `R4` (`MTU = 80`), donde los fragmentos que superan esos MTU vuelven a re-fragmentarse en trozos más chicos antes de llegar a `R5` y re-ensamblarse. Si el mismo paquete de 150 bytes se envía desde otros routers, cambia el tamaño y la cantidad inicial de fragmentos dependiendo del MTU del enlace de salida (por ejemplo, desde `R4` hacia `R5` el enlace directo tiene `MTU = 140`, por lo que se parte en solo 2 fragmentos sin necesidad de re-fragmentarse en el camino, mientras que desde `R3` los MTU son de `50` y `55`, dividiéndose en más fragmentos pequeños desde el primer salto).

A la hora de realizar las pruebas, se observa que los paquetes son capaces de ser fragmentados correctamente, incluso fragmentos logran ser fragmentados, y que al mandarlos desde otros router cambia el tamaño de estos pero no su comportamiendo, haciendo que al llegar todos a sus destino puedan ser emsamblados correctamente. Aun asi se observo que aun mandando los paquetes desde un router "Cercano" al del destino, el mensaje no lograba llegar completo por el descarte del ttl, con lo que se puede ver como al fragmentar los mensajes, al ser muchos fragmentos, prueban diferentes rutas debido al Round Robin, haciendo que un fragmento tome un camino mas largo al ttl inicial y haciendo que el mensaje se descarte pro completo.
