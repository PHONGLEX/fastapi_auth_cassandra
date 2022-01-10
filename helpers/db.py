import os
import pathlib
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine.connection import register_connection, set_default_connection

from . import config as conf
from .config import config

CLUSTER_BUNDLE = os.path.join(conf.BASE_DIR , "ignored" , "fastapi-auth.zip")


def get_cluster():
    cloud_config = {
        "secure_connect_bundle": CLUSTER_BUNDLE
    }
    auth_provider = PlainTextAuthProvider(config['ASTRA_CLIENT_ID'], config['ASTRA_CLIENT_SECRET'])
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    return cluster


def get_session():
    cluster = get_cluster()
    session = cluster.connect()
    register_connection(str(session), session=session)
    set_default_connection(str(session))
    return cluster.connect()
    