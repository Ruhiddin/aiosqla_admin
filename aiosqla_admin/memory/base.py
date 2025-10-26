from redisimnest import BaseCluster
from redisimnest import Key as K
from ..settings import Settings

from .detail import DetailCluster
from .list import ListCluster


class DashboardCluster:
    __prefix__ = "dash:{user_id}"

    model_name = K('model_name', None)
    lists = ListCluster
    detail = DetailCluster


class MemoryCluster(BaseCluster):
    """
    # dash
    ### This holds dash (dashboard) scenario data of Parent Cluster
    """
    __prefix__ = "memo"
    __ttl__ = Settings.DASHBOARD_TTL

    dashboard = DashboardCluster