# diagnostics.py
import importlib, sys, inspect
mod_name = "app.gui.dialogs.settings_dialog"

print("sys.path[0..5]:", sys.path[:6])
try:
    m = importlib.import_module(mod_name)
    print("Imported module file:", getattr(m, "__file__", "<no __file__>"))
    print("Attributes containing 'Settings':", [n for n in dir(m) if "Settings" in n])
    # show source lines around a class if defined
    if hasattr(m, "SettingsDialog"):
        print("SettingsDialog found:", m.SettingsDialog)
        print("Source snippet:")
        import inspect
        print("\n".join(inspect.getsource(m.SettingsDialog).splitlines()[:20]))
    else:
        print("SettingsDialog NOT found inside module.")
except Exception as e:
    print("Import failed:", type(e).__name__, e)
