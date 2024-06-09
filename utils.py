import httpx


def get_coordinates(location):
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
    response = httpx.get(url)
    data = response.json()
    if data:
        return (float(data[0]["lat"]), float(data[0]["lon"]))
    else:
        return None


def remove_vetrina_prefix(s):
    if s.startswith("Vetrina"):
        return s[len("Vetrina ") :]  # Remove the prefix and the space following it
    return s
