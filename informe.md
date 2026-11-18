# Fragmentación

## Implementación de fragmentación

Para esto, primero revisa si el tamaño de los headers con el mensaje sean igual o menores al MTU, con esto es capaz de ver si es posible de mandarlo completo, sino, toma la máxima porsión del mensaje y la separa. Con esta porsión se setea que su flag es 1, mientras que la otra porsión se setea un offset sumando el tamaño de la primera porsion a su offset, con esto nos aseguramos que si es un mensaje ya fragmentado, pueda mantener su posicion. Luego la primera parte se pone en un arreglo unico y se concatena con el resultado de aplicarle la funcion de fragmentacion a la segunda parte

## Implementación de Re-Emsamblado

Se setea una base de Paquete con la informacion que no cambia del mensaje original, y se setea su flag en 1 y el mensaje como vacio. Luego entra en un bucle usando un contador revisando cada segmento en el arreglo, si el tamaño del mensaje ya guardado es igual al offset, este se agrega al paquete base y se setea su flag como la flag de ese mensaje, de modo que si este era 0, significa que el mensaje termino, y vuelve la cuenta a 0. Si no encontro ningun mensaje que correspondiera al offset, se sale del bucle al superar el largo del arreglo y devuelve 0. Con eso se uso que un mensaje sin fragmentar tiene que tener su flag igual a 0.

## Desicion de diseño

Para el ensamblado, se tomo la desicion de que se guardara tambien el tamaño del mensaje asociado al id, con el fin de que solo cuando sepa que llego el mensaje completo intentara re-emsamblarlo. Esto debido a que al hacer pruebas, algunos paquetes se perdian, de modo que se considero que al tratar armar los paquetes de nuevo, el timpo usado para este pudo haber hecho que ignorara los mensajes en ese tiempo. Esto fue una suposicion, pero funciono al aplicarlo.

## Pruebas

A la hora de realizar las pruebas, se observa que los paquetes son capaces de ser fragmentados correctamente, incluso fragmentos logran ser fragmentados, y que al mandarlos desde otros router cambia el tamaño de estos pero no su comportamiendo, haciendo que al llegar todos a sus destino puedan ser emsamblados correctamente. Aun asi se observo que aun mandando los paquetes desde un router "Cercano" al del destino, el mensaje no lograba llegar completo por el descarte del ttl, con lo que se puede ver como al fragmentar los mensajes, al ser muchos fragmentos, prueban diferentes rutas debido al Round Robin, haciendo que un fragmento tome un camino mas largo al ttl inicial y haciendo que el mensaje se descarte pro completo.
