"""Utilities for database operations"""
import sqlite3

DATABASE = 'nn_database.db'


def get_connection():
    """Returns a connection to sqlite DB

    Returns: DB connection
    """
    conn = sqlite3.connect(DATABASE)
    return conn


def close_connection(conn):
    """Closes DB connection

    Args:
        conn: DB connection
    """
    if conn is not None:
        conn.close()


def rollback(conn):
    """Rolls DB operations back if connection is not None

    Args:
        conn: DB connection
    """
    if conn is not None:
        conn.rollback()


def init_db():
    """Initializes DB with necessary table(s)"""
    conn = None
    try:
        conn = get_connection()
        conn.execute(
            'CREATE TABLE IF NOT EXISTS neural_network (nn_id TEXT NOT NULL UNIQUE , n_layer INT NOT NULL , directory TEXT NOT NULL )')
    except sqlite3.Error:
        rollback(conn)
    finally:
        close_connection(conn)


def insert_neural_network(nn_id, n_layer, directory):
    """Inserts a new neural network definition into neural_network table

    Args:
        nn_id: Uniquely generated alpha numeric ID of the neural network
        n_layer: Number of hidden layers of the neural network
        directory:  Folder Path to store neural network structure
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO neural_network (nn_id, n_layer, directory) VALUES (?,?,?)",
                    (nn_id, n_layer, directory))
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
    finally:
        close_connection(conn)


def get_neural_network(nn_id):
    """Returns a neural network from DB by the given unique ID

    Args:
        nn_id: Uniquely generated alpha numeric ID of the neural network

    Returns:
        n_layer: Number of hidden layers of the neural network
        directory:  Folder Path to store neural network structure
    """
    conn = None
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT n_layer, directory FROM neural_network WHERE nn_id=?", (nn_id,))
        neural_network = cur.fetchone()
        if neural_network is not None:
            n_layers = neural_network[0]
            directory = neural_network[1]
            return n_layers, directory
        else:
            return None, None
    finally:
        close_connection(conn)
