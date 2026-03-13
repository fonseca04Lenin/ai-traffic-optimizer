"""
Route optimization engine using NetworkX and a priority-aware
nearest-neighbor heuristic (approximate TSP solver).

Priority weighting means high-priority jobs are treated as
"closer" during selection, so they naturally bubble to the
front of the route without a hard sort.
"""
import math
import networkx as nx


PRIORITY_WEIGHT = {'high': 0.5, 'normal': 1.0, 'low': 1.6}
AVG_SPEED_MPH  = 25.0   # average city driving speed
MINS_PER_STOP  = 12     # service time per stop


def haversine(lat1, lon1, lat2, lon2):
    """Great-circle distance between two GPS coordinates (miles)."""
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def build_graph(jobs):
    """
    Build a weighted complete graph where nodes are job IDs
    and edge weights are haversine distances between stops.
    """
    G = nx.Graph()
    for job in jobs:
        G.add_node(job.id, lat=job.latitude, lng=job.longitude, priority=job.priority)
    for i, a in enumerate(jobs):
        for b in jobs[i + 1:]:
            dist = haversine(a.latitude, a.longitude, b.latitude, b.longitude)
            G.add_edge(a.id, b.id, weight=dist)
    return G


def optimize_route(jobs, depot_lat=None, depot_lng=None):
    """
    Run priority-aware nearest-neighbor heuristic on the job list.

    Returns:
        ordered_jobs  – jobs in optimized visit order
        total_miles   – total route distance in miles
        duration_mins – estimated total time including stop time
        savings_pct   – % distance saved vs naive sequential order
    """
    valid = [j for j in jobs if j.has_coords()]
    if not valid:
        return list(jobs), 0.0, 0, 0.0

    G = build_graph(valid)
    job_map = {j.id: j for j in valid}
    remaining = set(j.id for j in valid)
    ordered = []

    # Seed: depot position or the highest-priority job
    if depot_lat is not None and depot_lng is not None:
        cur_lat, cur_lng = depot_lat, depot_lng
    else:
        seed = min(valid, key=lambda j: PRIORITY_WEIGHT[j.priority])
        ordered.append(seed)
        remaining.discard(seed.id)
        cur_lat, cur_lng = seed.latitude, seed.longitude

    # Greedy nearest-neighbor with priority scoring
    while remaining:
        best_id, best_score = None, float('inf')
        for jid in remaining:
            j = job_map[jid]
            dist = haversine(cur_lat, cur_lng, j.latitude, j.longitude)
            score = dist * PRIORITY_WEIGHT[j.priority]
            if score < best_score:
                best_score = score
                best_id = jid
        ordered.append(job_map[best_id])
        remaining.discard(best_id)
        cur_lat = job_map[best_id].latitude
        cur_lng = job_map[best_id].longitude

    # Total optimized distance
    total_miles = 0.0
    if depot_lat is not None and ordered:
        total_miles += haversine(depot_lat, depot_lng, ordered[0].latitude, ordered[0].longitude)
    for i in range(len(ordered) - 1):
        a, b = ordered[i], ordered[i + 1]
        total_miles += haversine(a.latitude, a.longitude, b.latitude, b.longitude)

    # Naive distance: jobs in original creation order
    naive_miles = 0.0
    naive = [j for j in jobs if j.has_coords()]
    for i in range(len(naive) - 1):
        naive_miles += haversine(naive[i].latitude, naive[i].longitude,
                                 naive[i + 1].latitude, naive[i + 1].longitude)

    savings_pct = 0.0
    if naive_miles > 0 and total_miles < naive_miles:
        savings_pct = (naive_miles - total_miles) / naive_miles * 100

    duration_mins = int((total_miles / AVG_SPEED_MPH) * 60) + len(ordered) * MINS_PER_STOP

    return ordered, round(total_miles, 2), duration_mins, round(savings_pct, 1)
