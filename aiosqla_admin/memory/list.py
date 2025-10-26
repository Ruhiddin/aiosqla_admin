from redisimnest import Key as K


class ListPagesDataCluster:
    """
    # pages_data
    ### This holds the collection of pages data of dashboard's list data
    """
    __prefix__ = 'pages_data'


    page_data = K('pg:{page}', [])


class ListCluster:
    """
    # list:{model_name}
    ### This holds page listing related data of a dashboard of a Parent Cluster
    """
    __prefix__ = 'list:{model_name}'


    list_click_mode = K('list_mode', True)

    table_count = K('table_count', None)
    current_count = K('current_count', None)

    filters = K('filters', {})
    sort_data = K('sort_data', {})

    pages_data = ListPagesDataCluster

