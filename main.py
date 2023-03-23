import sys
from USD_to_OWL import usd_to_owl

if __name__ == "__main__":
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
    else:
        print('Usage: file_path.usda')
        sys.exit(1)
    usd_to_owl(file_path)
