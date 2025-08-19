def safe_load(text):
    result = {}
    for line in text.strip().splitlines():
        if not line:
            continue
        k, v = line.split(":")
        result[k.strip()] = v.strip()
    return result
