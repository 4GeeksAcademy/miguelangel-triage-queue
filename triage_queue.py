from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


TRIAGE_LABELS: Dict[int, str] = {
    1: "Crítico",
    2: "Urgente",
    3: "Estándar",
}


@dataclass
class Patient:
    """Representa a un paciente en la unidad de urgencias."""

    name: str
    triage_level: int
    arrived_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("El nombre del paciente no puede estar vacío.")
        self.name = self.name.strip()

        if (
            isinstance(self.triage_level, bool)
            or not isinstance(self.triage_level, int)
            or self.triage_level not in (1, 2, 3)
        ):
            raise ValueError(
                "El nivel de triaje debe ser un entero entre 1 (crítico), 2 (urgente) o 3 (estándar)."
            )

    def __str__(self) -> str:
        label = TRIAGE_LABELS.get(self.triage_level, "Desconocido")
        timestamp = self.arrived_at.strftime("%H:%M:%S")
        return f"[Nivel {self.triage_level} - {label}] {self.name} (llegada: {timestamp})"


class TriageQueue:
    """Cola de prioridad para triaje hospitalario basada en deques por nivel."""

    VALID_LEVELS = (1, 2, 3)

    def __init__(self) -> None:
        self._queues: Dict[int, deque[Patient]] = {
            level: deque() for level in self.VALID_LEVELS
        }

    def enqueue(self, patient: Patient) -> None:
        """Añade un paciente a la cola respetando su nivel de triaje y orden de llegada."""
        if not isinstance(patient, Patient):
            raise TypeError("Solo se pueden encolar instancias de Patient.")
        if patient.triage_level not in self._queues:
            raise ValueError(f"Nivel de triaje inválido: {patient.triage_level}")
        self._queues[patient.triage_level].append(patient)

    def dequeue(self) -> Patient:
        """Extrae y devuelve el siguiente paciente a ser atendido.

        Lanza IndexError si la cola está vacía.
        """
        for level in self.VALID_LEVELS:
            if self._queues[level]:
                return self._queues[level].popleft()
        raise IndexError("No hay pacientes en espera en la cola de triaje.")

    def peek(self) -> Optional[Patient]:
        """Devuelve el siguiente paciente a ser atendido sin extraerlo, o None si está vacía."""
        for level in self.VALID_LEVELS:
            if self._queues[level]:
                return self._queues[level][0]
        return None

    def list_queue(self) -> List[Patient]:
        """Devuelve todos los pacientes en espera en el orden en que serán atendidos."""
        ordered_patients: List[Patient] = []
        for level in self.VALID_LEVELS:
            ordered_patients.extend(self._queues[level])
        return ordered_patients

    def stats(self) -> Dict[int, int]:
        """Devuelve un diccionario con el número de pacientes en espera por nivel de triaje."""
        return {level: len(self._queues[level]) for level in self.VALID_LEVELS}


def _prompt_new_patient(queue: TriageQueue) -> None:
    """Solicita los datos por consola y encola un nuevo paciente."""
    name = input("Nombre del paciente: ").strip()
    if not name:
        print("Error: El nombre del paciente no puede estar vacío.")
        return

    raw_level = input("Nivel de triaje (1 = Crítico, 2 = Urgente, 3 = Estándar): ").strip()
    try:
        level = int(raw_level)
        patient = Patient(name=name, triage_level=level)
    except ValueError:
        print("Error: Nivel de triaje inválido. Debe introducir 1, 2 o 3.")
        return

    queue.enqueue(patient)
    print(f"Paciente registrado correctamente: {patient}")


def _call_next_patient(queue: TriageQueue) -> None:
    """Extrae y muestra al siguiente paciente a ser atendido."""
    try:
        patient = queue.dequeue()
        print(f"Atendiendo a: {patient}")
    except IndexError as exc:
        print(f"Aviso: {exc}")


def _peek_next_patient(queue: TriageQueue) -> None:
    """Muestra quién es el siguiente paciente sin retirarlo de la cola."""
    patient = queue.peek()
    if patient is None:
        print("No hay pacientes en espera.")
    else:
        print(f"Siguiente paciente en espera: {patient}")


def _show_queue(queue: TriageQueue) -> None:
    """Muestra todos los pacientes en espera en orden de atención."""
    patients = queue.list_queue()
    if not patients:
        print("La cola de espera está vacía.")
        return

    print(f"\nPacientes en espera ({len(patients)} en total):")
    for idx, patient in enumerate(patients, start=1):
        print(f"  {idx}. {patient}")


def _show_stats(queue: TriageQueue) -> None:
    """Muestra el conteo de pacientes por nivel de triaje."""
    counts = queue.stats()
    total = sum(counts.values())
    print("\nEstadísticas de la cola:")
    for level in TriageQueue.VALID_LEVELS:
        label = TRIAGE_LABELS[level]
        print(f"  Nivel {level} ({label}): {counts[level]} paciente(s)")
    print(f"  Total en espera: {total} paciente(s)")


def main() -> None:
    """Ejecuta el menú interactivo de línea de comandos (CLI)."""
    queue = TriageQueue()

    while True:
        print("\n=== GESTOR DE COLA DE TRIAJE ===")
        print("1. Añadir nuevo paciente")
        print("2. Llamar al siguiente paciente")
        print("3. Ver siguiente paciente (peek)")
        print("4. Ver la cola actual")
        print("5. Ver estadísticas de la cola")
        print("6. Salir")

        choice = input("Seleccione una opción (1-6): ").strip()

        if choice == "1":
            _prompt_new_patient(queue)
        elif choice == "2":
            _call_next_patient(queue)
        elif choice == "3":
            _peek_next_patient(queue)
        elif choice == "4":
            _show_queue(queue)
        elif choice == "5":
            _show_stats(queue)
        elif choice == "6":
            print("Saliendo del gestor de triaje. ¡Hasta pronto!")
            break
        else:
            print("Opción no válida. Por favor, elija un número del 1 al 6.")


if __name__ == "__main__":
    main()
