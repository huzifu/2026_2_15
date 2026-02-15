try:
    import tkinter
    print("tkinter: ok")
except ImportError as e:
    print(f"tkinter: missing ({e})")

try:
    import jieba
    print("jieba: ok")
except ImportError as e:
    print(f"jieba: missing ({e})")

try:
    import PIL
    print("PIL: ok")
except ImportError as e:
    print(f"PIL: missing ({e})")

try:
    import sklearn
    print("sklearn: ok")
except ImportError as e:
    print(f"sklearn: missing ({e})")

try:
    import matplotlib
    print("matplotlib: ok")
except ImportError as e:
    print(f"matplotlib: missing ({e})")

print("Check complete")
