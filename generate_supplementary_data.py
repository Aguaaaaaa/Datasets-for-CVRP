"""Generate deterministic supplementary data for the truck-drone benchmarks."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


CUSTOMER_COUNTS = (6, 8, 10, 25, 50, 75, 100)
URGENCY_RATIO = 2
GRID_POINTS_PER_AXIS = 10
COORDINATE_MIN = 0.0
COORDINATE_MAX = 100.0
FLOAT_TOLERANCE = 1e-10


def format_number(value: float) -> str:
    """Return a compact, locale-independent decimal representation."""
    return format(value, ".15g")


def urgency_rows() -> list[tuple[int, int, float]]:
    rows: list[tuple[int, int, float]] = []
    for customer_count in CUSTOMER_COUNTS:
        odd_count = math.ceil(customer_count / 2)
        even_count = math.floor(customer_count / 2)
        denominator = URGENCY_RATIO * odd_count + even_count
        for customer_index in range(1, customer_count + 1):
            multiplier = 1 + (URGENCY_RATIO - 1) * (customer_index % 2)
            weight = customer_count * multiplier / denominator
            rows.append((customer_count, customer_index, weight))
    return rows


def grid_values() -> list[float]:
    step = (COORDINATE_MAX - COORDINATE_MIN) / (GRID_POINTS_PER_AXIS - 1)
    values = [COORDINATE_MIN + index * step for index in range(GRID_POINTS_PER_AXIS)]
    values[0] = COORDINATE_MIN
    values[-1] = COORDINATE_MAX
    return values


def rendezvous_rows() -> list[tuple[int, float, float]]:
    rows: list[tuple[int, float, float]] = []
    rendezvous_id = 1
    values = grid_values()
    for x in values:
        for y in values:
            rows.append((rendezvous_id, x, y))
            rendezvous_id += 1
    return rows


def validate_urgency(rows: list[tuple[int, int, float]]) -> None:
    expected_records = sum(CUSTOMER_COUNTS)
    if len(rows) != expected_records:
        raise ValueError(f"Expected {expected_records} urgency records, found {len(rows)}")

    for customer_count in CUSTOMER_COUNTS:
        group = [row for row in rows if row[0] == customer_count]
        indices = [row[1] for row in group]
        weights = [row[2] for row in group]
        if indices != list(range(1, customer_count + 1)):
            raise ValueError(f"Invalid customer indices for N={customer_count}")
        if not math.isclose(math.fsum(weights), customer_count, abs_tol=FLOAT_TOLERANCE):
            raise ValueError(f"Urgency weights do not sum to N for N={customer_count}")

        odd_weights = {weight for _, index, weight in group if index % 2 == 1}
        even_weights = {weight for _, index, weight in group if index % 2 == 0}
        if len(odd_weights) != 1 or len(even_weights) != 1:
            raise ValueError(f"Inconsistent urgency levels for N={customer_count}")
        odd_weight = next(iter(odd_weights))
        even_weight = next(iter(even_weights))
        if not math.isclose(odd_weight / even_weight, URGENCY_RATIO, abs_tol=FLOAT_TOLERANCE):
            raise ValueError(f"Urgency ratio is not 2:1 for N={customer_count}")


def validate_rendezvous(rows: list[tuple[int, float, float]]) -> None:
    if len(rows) != GRID_POINTS_PER_AXIS**2:
        raise ValueError(f"Expected 100 rendezvous nodes, found {len(rows)}")
    if [row[0] for row in rows] != list(range(1, 101)):
        raise ValueError("Rendezvous IDs must be consecutive from 1 to 100")

    coordinates = {(x, y) for _, x, y in rows}
    if len(coordinates) != len(rows):
        raise ValueError("Rendezvous coordinates contain duplicates")
    if not all(
        COORDINATE_MIN <= coordinate <= COORDINATE_MAX
        for _, x, y in rows
        for coordinate in (x, y)
    ):
        raise ValueError("A rendezvous coordinate is outside [0, 100]^2")


def write_urgency_csv(path: Path, rows: list[tuple[int, int, float]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("customer_count", "customer_index", "urgency_weight"))
        writer.writerows(
            (customer_count, customer_index, format_number(weight))
            for customer_count, customer_index, weight in rows
        )


def write_rendezvous_csv(path: Path, rows: list[tuple[int, float, float]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("rendezvous_id", "x", "y"))
        writer.writerows(
            (rendezvous_id, format_number(x), format_number(y))
            for rendezvous_id, x, y in rows
        )


def generate(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    urgency = urgency_rows()
    rendezvous = rendezvous_rows()
    validate_urgency(urgency)
    validate_rendezvous(rendezvous)
    write_urgency_csv(output_dir / "urgency_weights.csv", urgency)
    write_rendezvous_csv(output_dir / "rendezvous_coordinates.csv", rendezvous)
    print(f"Wrote {len(urgency)} urgency records and {len(rendezvous)} rendezvous records to {output_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory for the generated CSV files (default: script directory)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    generate(parse_args().output_dir.resolve())
