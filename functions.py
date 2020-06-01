def roundToNearestInt(val):
    decimal_part = val - int(val)
    if decimal_part <= 0.5:
        return int(val)
    else:
        return int(val) + 1