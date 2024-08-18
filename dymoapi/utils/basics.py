class DotDict(dict):
    def __init__(self, dct):
        for key, value in dct.items():
            if isinstance(value, dict): self[key] = DotDict(value)
            else: self[key] = value

    def __getattr__(self, key):
        try: return self[key]
        except KeyError: raise AttributeError(f"'DotDict' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try: del self[key]
        except KeyError: raise AttributeError(f"'DotDict' object has no attribute '{key}'")