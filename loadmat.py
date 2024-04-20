import scipy.io as sio
import gzip
import pickle
from os import path

main_folder = './'


def set_folder(folder):
    global main_folder
    main_folder = folder


def load_mat(fname, key=None, use_main_folder=True):
    global main_folder
    if use_main_folder:
        fname = main_folder + fname
    data = sio.loadmat(fname)
    if key == 'all':
        return data
    if key is None:
        key = list(data.keys())[3]
    return data[key].squeeze()


def save_mat(fname, dict_data, use_main_folder=True):
    global main_folder
    if use_main_folder:
        fname = main_folder + fname
    sio.savemat(fname, dict_data)


def save_fig(plt, fname, **kargs):
    global main_folder
    plt.savefig(main_folder + fname, **kargs)


def pickle_load(fname, use_main_folder=True):
    global main_folder
    if use_main_folder:
        fname = main_folder + fname
    try:
        if 'pklz' in fname:
            with gzip.open(fname, 'rb') as f:
                return pickle.load(f)
        else:
            with open(fname, 'rb') as f:
                return pickle.load(f)
    except:
        return None


def pickle_dump(fname, genNeighbors, zipped, use_main_folder=True):
    global main_folder
    if use_main_folder:
        fname = main_folder + fname
    if zipped:
        with gzip.open(fname, 'wb') as f:
            pickle.dump(genNeighbors, f, pickle.HIGHEST_PROTOCOL)
    else:
        with open(fname, 'wb') as f:
            pickle.dump(genNeighbors, f, pickle.HIGHEST_PROTOCOL)


def view_save_as_html(view, fname):
    global main_folder
    view.save_as_html(main_folder + fname)


def path_exists(fname, use_main_folder=True):
    global main_folder
    if use_main_folder:
        fname = main_folder + fname
    return path.exists(fname)
