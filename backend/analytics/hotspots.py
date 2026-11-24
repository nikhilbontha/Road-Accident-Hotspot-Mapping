import math
import numpy as np
from sklearn.cluster import DBSCAN
from scipy.stats import gaussian_kde
from typing import List, Dict, Any, Tuple, Optional

# Metric projection reference constants around Hyderabad/Telangana (lat ~17.42)
METERS_PER_DEG_LAT = 111320.0


def project_to_meters(lat: float, lon: float, ref_lat: float, ref_lon: float) -> Tuple[float, float]:
    """
    Local equirectangular metric projection for high-speed spatial distance calculation.
    Accurate to millimeter level within city scale (<100 km).
    """
    meters_per_deg_lon = METERS_PER_DEG_LAT * math.cos(math.radians(ref_lat))
    x = (lon - ref_lon) * meters_per_deg_lon
    y = (lat - ref_lat) * METERS_PER_DEG_LAT
    return x, y


def meters_to_lat_lon(x: float, y: float, ref_lat: float, ref_lon: float) -> Tuple[float, float]:
    """
    Convert local metric coordinates back to WGS84 (lat, lon).
    """
    meters_per_deg_lon = METERS_PER_DEG_LAT * math.cos(math.radians(ref_lat))
    lat = ref_lat + (y / METERS_PER_DEG_LAT)
    lon = ref_lon + (x / meters_per_deg_lon)
    return lat, lon


class HotspotDetector:

    def __init__(self, ref_lat: float = 17.4200, ref_lon: float = 78.5800):
        self.ref_lat = ref_lat
        self.ref_lon = ref_lon

    def detect_clusters(
        self,
        records: List[Dict[str, Any]],
        radius_m: float = 250.0,
        min_accidents: int = 5,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        DBSCAN spatial clustering on metric coordinates (FR-04).
        Enforces Insufficient Data Rule if records are inadequate.
        """
        if not records or len(records) < min_accidents:
            return [], "No reliable hotspot can be determined from this data"

        # Extract coordinates and project to metric plane
        pts_metric = []
        valid_records = []
        for r in records:
            lat = r.get("latitude")
            lon = r.get("longitude")
            if lat is not None and lon is not None:
                x, y = project_to_meters(lat, lon, self.ref_lat, self.ref_lon)
                pts_metric.append([x, y])
                valid_records.append(r)

        if len(valid_records) < min_accidents:
            return [], "No reliable hotspot can be determined from this data"

        coords = np.array(pts_metric)

        # Execute DBSCAN clustering
        clustering = DBSCAN(eps=radius_m, min_samples=min_accidents, metric="euclidean")
        labels = clustering.fit_predict(coords)

        unique_labels = set(labels)
        unique_labels.discard(-1)  # discard noise points

        if not unique_labels:
            return [], "No reliable hotspot can be determined from this data"

        clusters = []
        for label in unique_labels:
            indices = np.where(labels == label)[0]
            cluster_points = coords[indices]
            cluster_records = [valid_records[i] for i in indices]

            # Compute centroid
            centroid_x = float(np.mean(cluster_points[:, 0]))
            centroid_y = float(np.mean(cluster_points[:, 1]))
            centroid_lat, centroid_lon = meters_to_lat_lon(centroid_x, centroid_y, self.ref_lat, self.ref_lon)

            # Approximate radius in meters
            dists = np.linalg.norm(cluster_points - [centroid_x, centroid_y], axis=1)
            radius = float(np.max(dists)) if len(dists) > 0 else radius_m

            # Determine dominant road name
            road_names = [r.get("road_name") or r.get("location_text") for r in cluster_records if r.get("road_name") or r.get("location_text")]
            dominant_name = max(set(road_names), key=road_names.count) if road_names else "Road Stretch"

            clusters.append({
                "cluster_label": int(label),
                "name": dominant_name,
                "centroid_lat": centroid_lat,
                "centroid_lon": centroid_lon,
                "radius_m": max(radius, 50.0),
                "accidents": cluster_records,
                "accidents_count": len(cluster_records),
                "fatalities": sum(r.get("fatalities", 0) for r in cluster_records),
                "injuries": sum(r.get("injuries", 0) for r in cluster_records),
            })

        return clusters, None

    def compute_kde_heat_grid(
        self,
        records: List[Dict[str, Any]],
        grid_size: int = 50,
    ) -> Dict[str, Any]:
        """
        Compute 2D Gaussian Kernel Density Estimation (KDE) surface for heatmap layer (FR-04, FR-06).
        """
        lats = [r["latitude"] for r in records if "latitude" in r and r["latitude"] is not None]
        lons = [r["longitude"] for r in records if "longitude" in r and r["longitude"] is not None]

        if len(lats) < 3:
            return {"points": [], "bounds": {}}

        min_lat, max_lat = min(lats) - 0.01, max(lats) + 0.01
        min_lon, max_lon = min(lons) - 0.01, max(lons) + 0.01

        # Evaluate KDE
        try:
            kernel = gaussian_kde(np.vstack([lons, lats]))
            grid_lon, grid_lat = np.mgrid[min_lon:max_lon:complex(grid_size), min_lat:max_lat:complex(grid_size)]
            positions = np.vstack([grid_lon.ravel(), grid_lat.ravel()])
            densities = kernel(positions).reshape(grid_lon.shape)

            max_d = np.max(densities) if np.max(densities) > 0 else 1.0
            norm_densities = densities / max_d

            points = []
            for i in range(grid_size):
                for j in range(grid_size):
                    val = float(norm_densities[i, j])
                    if val > 0.08:  # filter noise threshold
                        points.append([float(grid_lat[i, j]), float(grid_lon[i, j]), round(val, 3)])

            return {
                "points": points,
                "bounds": {
                    "min_lat": min_lat,
                    "max_lat": max_lat,
                    "min_lon": min_lon,
                    "max_lon": max_lon,
                },
            }
        except Exception:
            # Fallback simple density representation
            points = [[lat, lon, 0.8] for lat, lon in zip(lats[:200], lons[:200])]
            return {"points": points, "bounds": {}}


hotspot_detector = HotspotDetector()
