import csv
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def calculate_distance(p1: List[float], p2: List[float]) -> float:
    """Calculates 2D Euclidean distance using math.hypot to avoid numeric overflow."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def normalize_input_data(data: Dict[str, Any]) -> Tuple[Dict[str, List[float]], Dict[str, List[float]], List[Dict[str, Any]]]:
    """
    Defensively normalizes input schemas.
    Supports both array-of-objects and key-value dictionary formats,
    as well as 'warehouse' vs 'warehouse_id' package keys.
    """
    warehouses: Dict[str, List[float]] = {}
    raw_wh = data.get("warehouses", {})
    if isinstance(raw_wh, list):
        for entry in raw_wh:
            warehouses[entry["id"]] = entry["location"]
    else:
        warehouses = raw_wh

    agents: Dict[str, List[float]] = {}
    raw_ag = data.get("agents", {})
    if isinstance(raw_ag, list):
        for entry in raw_ag:
            agents[entry["id"]] = entry["location"]
    else:
        agents = raw_ag

    packages: List[Dict[str, Any]] = []
    for pkg in data.get("packages", []):
        wh_key = pkg.get("warehouse") or pkg.get("warehouse_id")
        packages.append({
            "id": pkg["id"],
            "warehouse": wh_key,
            "destination": pkg["destination"]
        })

    return warehouses, agents, packages


def run_simulation(data: Dict[str, Any]) -> Dict[str, Any]:
    """Assigns packages to nearest agents and simulates multi-leg itineraries."""
    warehouses, agents, packages = normalize_input_data(data)
    agent_packages: Dict[str, List[Dict[str, Any]]] = {
        a_id: [] for a_id in agents}

    # Step 1: Nearest-agent assignment by Euclidean distance (Agent -> Warehouse)
    for pkg in packages:
        wh_loc = warehouses[pkg["warehouse"]]
        nearest_agent = min(
            agents.keys(),
            key=lambda a_id: (calculate_distance(agents[a_id], wh_loc), a_id)
        )
        agent_packages[nearest_agent].append(pkg)

    # Step 2: Simulate multi-leg delivery routes
    report: Dict[str, Any] = {}
    best_agent_id = None
    best_efficiency = float("inf")

    for agent_id, assigned_list in sorted(agent_packages.items()):
        current_loc = list(agents[agent_id])
        total_dist = 0.0

        for pkg in assigned_list:
            wh_loc = warehouses[pkg["warehouse"]]
            dest_loc = pkg["destination"]

            # Current position -> Warehouse -> Destination
            total_dist += calculate_distance(current_loc, wh_loc)
            total_dist += calculate_distance(wh_loc, dest_loc)
            current_loc = dest_loc

        delivered_count = len(assigned_list)
        efficiency = (
            total_dist / delivered_count) if delivered_count > 0 else 0.0

        report[agent_id] = {
            "packages_delivered": delivered_count,
            "total_distance": round(total_dist, 2),
            "efficiency": round(efficiency, 2)
        }

        if delivered_count > 0 and efficiency < best_efficiency:
            best_efficiency = efficiency
            best_agent_id = agent_id

    report["best_agent"] = best_agent_id
    return report


def export_best_agent_to_csv(report: Dict[str, Any], filename: str = "best_agent.csv") -> None:
    """Bonus: Exports top performer metrics to CSV."""
    best_id = report.get("best_agent")
    if not best_id or best_id not in report:
        return
    stats = report[best_id]
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["agent_id", "packages_delivered",
                        "total_distance", "efficiency"])
        writer.writerow([best_id, stats["packages_delivered"],
                        stats["total_distance"], stats["efficiency"]])


def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else "base_case.json"
    file_path = Path(input_file)

    if not file_path.exists():
        print(f"Error: {input_file} not found.")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    report = run_simulation(data)

    with open("report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    export_best_agent_to_csv(report)
    print(f"Processed {input_file} -> Saved to report.json and best_agent.csv")
    print(json.dumps(report, indent=4))


if __name__ == "__main__":
    main()
