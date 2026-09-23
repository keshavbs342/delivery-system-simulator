# FastBox Delivery System Logistics Simulator

A Python-based simulation engine for FastBox delivery logistics, modeling multi-warehouse distribution, nearest-agent assignments, multi-leg routing, and operational efficiency analysis.

## Key Design & Engineering Assumptions

1. **Schema Normalization**: Dynamically handles both list-of-objects (`base_case.json`) and key-value mapping structures (`test_case_*.json`), as well as schema variations like `warehouse` vs `warehouse_id`.
2. **Nearest-Agent Mapping**: Each package is mapped to the closest agent based on the 2D Euclidean distance from the agent's initial position to the package's originating warehouse. Equidistant ties are resolved deterministically by ascending Agent ID (`A1` < `A2`).
3. **Multi-Leg Route Sequence**: Agents travel sequentially: `Current Position -> Warehouse -> Destination`. An agent persists at the drop-off destination for subsequent pickups.
4. **Efficiency Formulation**: `Efficiency = Total Distance / Packages Delivered`. Lower values indicate higher fuel/travel efficiency. Idle agents (0 deliveries) receive `0.00` and are ineligible for `best_agent`.

## Bonus Features Included

- **CSV Export**: Automatically writes top-performing agent metrics to `best_agent.csv`.

## Execution

### Run Simulation

```bash
python simulator.py base_case.json
python simulator.py test_case_1.json
```
