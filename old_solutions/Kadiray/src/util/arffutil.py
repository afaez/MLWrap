"""Utilities for arff file format operations"""
import arff
import numpy as np

one_hot = {}


def get_data(file_directory):
    """Returns arff data

    Returns:
        data: arff formatted data
    """
    file = open(file_directory)
    data = arff.load(file)
    return data


def get_n_attributes(data):
    """Returns attribute list from data

    Args:
        data: arff data

    Returns:
        attributes: list of attributes
    """
    attributes = data['attributes']
    index_of_class = [y[0] for y in attributes].index('class')

    return len(attributes[:index_of_class]) - 1


def get_n_classes(data):
    """Returns class/label list from data

    Args:
        data: arff data

    Returns:
        classes: list of classes/labels
    """
    attributes = data['attributes']
    classes = dict(attributes)['class']
    class_to_one_hot(classes)
    return len(classes)


def get_batch_attributes(data, batch_start, batch_end, n_attributes):
    """Returns attribute values for given range of batch

    Args:
        data: arrf data
        batch_start: batch start index
        batch_end: batch end index
        n_attributes: number of attributes

    Returns:
        batch: batch of attributes values
    """
    batch_data = data['data'][batch_start:batch_end]
    batch = []
    for i in range(len(batch_data)):
        batch.append(batch_data[i][:n_attributes])
    return batch


def get_batch_classes(data, batch_start, batch_end):
    """Returns class values for given range of batch

    Args:
        data: arrf data
        batch_start: batch start index
        batch_end: batch end index

    Returns:
        classes: batch of class values
    """
    batch_data = data['data'][batch_start:batch_end]
    classes = []
    for i in range(len(batch_data)):
        classes.append(one_hot[batch_data[i][len(batch_data[i]) - 1]])
    return classes


def class_to_one_hot(classes):
    """Creates a mapping between a class/label value and its corresponding one hot array

    Args:
        classes: list of classes/labels

    Returns:
        one_hot: a dictionary of class value and its one hot array

    Example:
        {[Class_a, [1000]], [Class_b, [0100]], ...}
    """
    global one_hot
    for i in range(len(classes)):
        hots = []
        for j in range(len(classes)):
            if i == j:
                hots.append(1)
            else:
                hots.append(0)
        one_hot[classes[i]] = hots
    return one_hot


def one_hot_to_values():
    """Returns a mapping between class value and its one hot index from one hot array

    Returns:
        index_to_label: a dictionary of one hot index and corresponding class value

    Example:
        {[1, Class_a], [2, Class_b], ...}
    """
    global one_hot
    index_to_label = {}
    for key, value in one_hot.items():
        index = np.argmax(value)
        index_to_label[index] = key
    return index_to_label
