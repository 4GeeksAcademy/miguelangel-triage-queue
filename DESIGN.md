# Notas de Diseño — Gestor de Cola de Prioridad de Triaje (`TriageQueue`)

## 1. Elección de la estructura de datos interna

Se utiliza un diccionario con tres instancias de `collections.deque` separadas, una por cada nivel de triaje (`{1: deque(), 2: deque(), 3: deque()}`):

- **Frente a una sola `deque` o lista ordenada:** Insertar un paciente de nivel 1 o 2 en medio de una secuencia única requiere desplazar elementos en $O(n)$ o reordenar la lista en $O(n \log n)$. Con tres `deque` separadas, tanto `enqueue` (`append`) como `dequeue` (`popleft`) ocurren en tiempo constante $O(1)$, ya que el número de niveles de prioridad (3) es fijo y pequeño.
- **Frente a `heapq` (montículo binario):** Un heap opera en $O(\log n)$ por inserción/extracción y no garantiza estabilidad FIFO por sí solo cuando las prioridades empatan (requiere mantener una tupla con un contador incremental de desempate). Con tres `deque` separadas:
  - El orden de llegada (FIFO) dentro de cada nivel se preserva de forma natural.
  - `peek()` es $O(1)$.
  - `stats()` se calcula en $O(1)$ consultando `len()` sobre cada `deque` sin recorrer toda la cola.

## 2. Gestión de concurrencia y orden de mutación del estado

En un escenario donde un worker extrae un paciente (`dequeue`) en el mismo instante en que otro worker encola un nuevo paciente crítico de nivel 1 (`enqueue`):

1. **Exclusión mutua (`threading.Lock`):** Ambos métodos (`enqueue` y `dequeue`) deben proteger el acceso a las colas internas mediante un mismo cerrojo (`with self._lock:`). Como cada operación sobre la `deque` es $O(1)$, la sección crítica dura apenas nanosegundos:
   - Si `enqueue` adquiere el lock primero, el paciente crítico de nivel 1 queda insertado antes de que `dequeue` evalúe las colas, por lo que `dequeue` lo atenderá inmediatamente.
   - Si `dequeue` adquiere el lock primero, extraerá al paciente más prioritario presente en ese instante exacto y, acto seguido, `enqueue` registrará al nuevo paciente crítico como el primero para la siguiente llamada.
2. **Orden de mutación para evitar el doble procesamiento:** El estado de la cola debe mutarse **antes** de devolver o procesar al paciente. Dentro del bloque protegido por el lock, primero se ejecuta `popleft()` (eliminando la referencia del paciente de la `deque` interna) y solo después se libera el lock y se entrega el objeto `Patient` al worker. De esta forma, ningún otro worker concurrente podrá observar ni extraer al mismo paciente dos veces.
