from redisimnest import Key as K



class DetailStackInstanceDataCluster:
    """
    # instance:{model_name}-{id}
    ### This holds the instance data
    """
    __prefix__ = 'instance:{model_name}-{id}'

    data = K('data', {})
    current_field = K('current_field', None)
    current_field_ui_text = K('cur_fil_ui_text', None)



class DetailStackCluster:
    """
    # stack
    ### holds the data of detail stack of a dashboard
    """
    __prefix__ = 'stack'
    
    stack_list = K("stack_list", [])
    instance = DetailStackInstanceDataCluster


class DetailCluster:
    """
    # detail
    """
    __prefix__ = 'detail'


    model_name = K('model_name', None)
    navigation_text = K("navigation_text", None)
    navigation_msg_id = K("navigation_msg_id", None)

    stack = DetailStackCluster

