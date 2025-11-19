import importlib.util
import importlib.metadata
import subprocess
import sys

def run_pip_command(args):
    try:
        subprocess.check_call([sys.executable, "-m", "ensurepip"])
        subprocess.check_call([sys.executable, "-m", "pip"] + args)
        return True, ""
    except Exception as e:
        return False, str(e)

class Dependency:
    def __init__(self, package_name, gui_name=None, import_name=None):
        self.package_name = package_name
        self.import_name = import_name or package_name
        self.gui_name = gui_name or package_name.title()

    def is_installed(self):
        return importlib.util.find_spec(self.import_name) is not None

    def get_version_and_location(self):
        try:
            dist = importlib.metadata.distribution(self.package_name)
            return dist.version, str(dist.locate_file(''))
        except Exception:
            return "N/A", ""