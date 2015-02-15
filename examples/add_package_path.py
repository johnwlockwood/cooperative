import sys
import os

package_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))

if package_path not in sys.path:
    sys.path.append(package_path)
