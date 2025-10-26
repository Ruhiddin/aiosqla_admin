from sqlalchemy import select







async def select_page_data(Model, page: int, items_per_page: int=10):
    """
    Handles pagination for a SQLAlchemy model.

    :param Model: SQLAlchemy model class for which data is being fetched.
    :param page: Current page number (1-based index).
    :return: stmt (page selection)
    """
    
    offset = (page - 1) * items_per_page

    stmt = select(Model).limit(items_per_page).offset(offset)
    return stmt

