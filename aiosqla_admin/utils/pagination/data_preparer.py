from sqlalchemy.ext.asyncio import AsyncSession
from redisimnest import BaseCluster
from aiogram.types import Message
from aiogram.filters.callback_data import CallbackData
from enum import Enum

from aiogram_toolkit.markdown.wrappers.markdown_v2 import link
from ...memory.base import MemoryCluster

from aiogram_toolkit.sqla_dashboard.utils.instance import get_current_instance_, hydrate_instance_from_data


async def get_current_instance_related_ids(message: Message, memory: MemoryCluster, session: AsyncSession):
    [model_name, __], instance_data, current_field = await get_current_instance_(memory, ['model_name_and_id', 'data', 'current_field'])

    if not [model_name or current_field or instance_data]:
        return await message.edit_text('Aloqa darchasi eskirgan yoki kutilmagan xatolik!')
    
    instance = await hydrate_instance_from_data(model_name, instance_data, session)

    rel_objects = getattr(instance, current_field, [])
    ids = [obj.id for obj in rel_objects] if isinstance(rel_objects, list) else [rel_objects.id] if rel_objects else []
    return ids



async def get_page_data(
        stmt, 
        model_name: str, 
        page: int, 
        session: AsyncSession, 
        memory: BaseCluster, 
        msg: Message, 
        list_click_mode: bool, 
        Callback: CallbackData, 
        trigger: Enum, 
        action: Enum, 
        is_selection: bool
    ):
    """
    Fetches paginated page data for a SQLAlchemy model with caching.

    - Retrieves data from FSMContext cache if available.
    - Executes the provided SQLAlchemy statement if the page is not cached.
    - Stores fetched results in FSMContext for future requests.

    :param stmt: SQLAlchemy query statement.
    :param model_name: Name of the model (used for cache key).
    :param page: Page number (1-based index).
    :param session: SQLAlchemy session object.
    :param memory: Dashboard cluster instance
    :param msg: Message
    :param list_click_mode: bool
    :param Callback: Aiogram's CallackData util
    :param trigger: Trigger enum option
    :param action: Action enum option
    :param is_selection: bool
    :return: Cached or freshly fetched list of objects.
    """

    page_data = await memory.lists(model_name).pages_data.page_data(page).get()
    if page_data:
        return page_data
    
    await msg.edit_text(f'Downloading {model_name}: {page}-page...')

    ids = await get_current_instance_related_ids(msg, memory, session) if is_selection else []


    page_data = []
    for model in await session.scalars(stmt):
        if list_click_mode:
            string = link(label=model.tg_list_view(), url=await Callback(action=action.__class__.MODEL_PREVIEW, reply_msg_id=msg.message_id, class_name=model_name, id=model.id).generate_deeplink(msg.bot))
        else:
            string = model.tg_list_view()
        
        checkmark = '✅ ' if model.id in ids and is_selection else ''
        string = checkmark + string
        
        page_data.append({
            'string': string,
            'label': str(model.id),
            'cd': Callback(triggers=trigger, action=action, mdl_name=model_name, id=model.id).pack()
        })

    if page_data:
        await memory.lists(model_name).pages_data.page_data(page).set(page_data)
    return page_data
