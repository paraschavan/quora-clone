import os
import re
import sys

try:
    import django

    print(f"Django is installed, version: {django.get_version()}")
except ImportError:
    print("Django is not installed.")
    sys.exit(1)


def get_django_root(start_path):
    current_path = start_path
    while True:
        parent_path = os.path.dirname(current_path)
        os.chdir(current_path)
        for item in os.listdir(current_path):
            if os.path.isfile(item):
                if item == "manage.py":
                    return current_path

        if parent_path == current_path:
            break
        current_path = parent_path


def find_settings_module(manage_py_path):
    with open(manage_py_path, "r") as file:
        content = file.read()
        match = re.search(
            r"os\.environ\.setdefault\(\"DJANGO_SETTINGS_MODULE\", \"(.+?)\"\)", content
        )
        if match:
            return match.group(1)
        else:
            raise Exception("DJANGO_SETTINGS_MODULE not found in manage.py")


start_path = os.path.dirname(os.path.abspath(__file__))
root = get_django_root(start_path)

if root is None:
    raise Exception("Django root not found")

manage_py_path = os.path.join(root, "manage.py")
settings_module = find_settings_module(manage_py_path)

sys.path.insert(0, root)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

django.setup()

print(f"Playground is ready with settings module: {settings_module}")
