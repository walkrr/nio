import json
import os
import pickle as unsafepickle

from safepickle import safepickle as pickle


def load_json(path):
    """ Loads a file in json format

    Args:
        path (str): path to file

    Returns:
        file contents as a dictionary
    """
    data = {}
    if os.path.isfile(path):
        with open(path, 'r') as f:
            data = json.loads(f.read())
    return data


def save_json(path, data):
    """ Saves a file in json format

    Args:
        path (str): path to file
        data (dict): data to save

    """
    with open(path, 'w+') as f:
        json.dump(data, f,
                  indent=4, separators=(',', ': '), sort_keys=True)


def load_pickle(path):
    """ Loads a file in pickle format

    Args:
        path (str): path to file

    Returns:
        file contents as a dictionary
    """
    data = {}
    if os.path.isfile(path):
        try:
            with open(path, 'r') as f:
                data = pickle.load(f)
        except:
            # TODO: this will be eventually removed once there is certainty
            # that all nio instances have been migrated to using safepickle
            with open(path, 'rb') as f:
                data = unsafepickle.load(f)
    return data


def save_pickle(path, data):
    """ Saves a file in pickle format

    Args:
        path (str): path to file
        data (dict): data to save

    """
    with open(path, 'w+') as f:
        pickle.dump(data, f)
