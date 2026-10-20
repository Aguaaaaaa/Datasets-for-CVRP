# Truck-Drone Collaborative Delivery Benchmark Data

## Dataset Description

This dataset contains 56 modified Solomon instances in `SolomonDataset.xlsx` and 25 modified Poikonen instances in `PoikonenDataset.xlsx`. It is intended for experiments on a collaborative truck-drone delivery system. Each worksheet represents one benchmark instance and contains 101 rows and four columns. The first row represents the depot, and the following 100 rows represent customers indexed from 1 to 100. Columns A-D contain the horizontal coordinate, vertical coordinate, customer demand, and service time, respectively.

The tested customer counts are `N = {6, 8, 10, 25, 50, 75, 100}`. An instance with fewer than 100 customers is constructed by selecting customers 1 through `N` from the corresponding worksheet, while retaining the worksheet's depot row. The two Excel workbooks are source data and are not modified by the supplementary-data generation script.

## Urgency Weight Generation

Customer urgency weights use a 2:1 ratio between odd- and even-indexed customers. For a customer count `N`, customer `i` receives

```text
U_i = N[1 + (UR - 1) mod(i, 2)] / [UR ceil(N/2) + floor(N/2)],
where UR = 2 and i = 1, ..., N.
```

The weights are normalized so that their sum equals `N`, which gives an average urgency weight of one for every tested customer count. The normalization accounts for unequal group sizes when `N` is odd. For even `N`, odd-indexed customers have weight `4/3` and even-indexed customers have weight `2/3`.

`urgency_weights.csv` contains the fields `customer_count`, `customer_index`, and `urgency_weight`. It contains 274 data records covering all seven tested customer counts. The sequence for a given customer count is shared by all benchmark instances.

## Candidate Rendezvous Node Generation

The 100 candidate rendezvous nodes form a deterministic uniform grid over the square service region `[0,100] x [0,100]`. Each axis uses the ten equally spaced values produced by `linspace(0,100,10)`, including both boundaries. The Cartesian product of these values forms a `10 x 10` grid. The grid is shared by all 81 benchmark instances and requires no random seed.

`rendezvous_coordinates.csv` contains the fields `rendezvous_id`, `x`, and `y`. IDs run from 1 to 100. The ordering is x-major: one x-coordinate is fixed while all ten y-coordinates are traversed in increasing order, after which the next x-coordinate is used.

## Reproduction

The CSV files can be regenerated with Python 3 using only the standard library:

```shell
python generate_supplementary_data.py
```

By default, the script writes both CSV files beside the script. A different output directory can be supplied with `--output-dir PATH`. The script validates the expected urgency-record count, each group's normalized sum and 2:1 ratio, and the rendezvous grid's size, uniqueness, ID sequence, and coordinate bounds before writing the files.

## File Inventory

- `SolomonDataset.xlsx`: 56 source benchmark worksheets; unchanged by generation.
- `PoikonenDataset.xlsx`: 25 source benchmark worksheets; unchanged by generation.
- `urgency_weights.csv`: normalized urgency weights for the seven tested customer counts.
- `rendezvous_coordinates.csv`: 100 deterministic candidate rendezvous coordinates.
- `generate_supplementary_data.py`: reproducible generator and validation script for both CSV files.
