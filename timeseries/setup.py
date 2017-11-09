import pip
import importlib

def install(package):
    try:
        importlib.import_module(package)
    except ImportError:
        pip.main(['install', package])


if __name__ == '__main__':
    install('numpy')
    install('pandas')
    install('statsmodels')
    install('matplotlib')
    install('scipy')

