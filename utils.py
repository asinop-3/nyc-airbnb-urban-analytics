# this file will contain any helper code

def point_in_ring(lon, lat, ring):
    """
    Return True if (lon, lat) is inside a polygon ring (list of [lon, lat] points).
    Uses ray casting algorithm.
    """
    inside = False
    n = len(ring)
    if n < 3:
        return False

    x = lon
    y = lat

    for i in range(n):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % n]

        # Check if the horizontal ray at y intersects the edge
        if (y1 > y) != (y2 > y):
            denom = (y2 - y1)
            if denom == 0:
                continue
            x_int = x1 + (y - y1) * (x2 - x1) / denom
            if x_int > x:
                inside = not inside

    return inside


def point_in_district(lon, lat, rings):
    """
    Return True if point is inside ANY of the rings for a district.
    """
    for ring in rings:
        if point_in_ring(lon, lat, ring):
            return True
    return False