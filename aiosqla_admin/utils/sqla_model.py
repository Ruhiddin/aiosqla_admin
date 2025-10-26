from aiogram_toolkit.dashboard.utils.dashboard_instance import get_current_instance_, hydrate_instance_from_data
from aiogram_toolkit.dashboard.memory.base import BaseCluster
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message





# ==============______GET CURRENT INSTANCE RELATED IDS______=========================================================================================== GET CURRENT INSTANCE RELATED IDS
async def get_current_instance_related_ids(message: Message, dashboard: BaseCluster, session: AsyncSession):
    [model_name, __], instance_data, current_field = await get_current_instance_(dashboard, ['model_name_and_id', 'data', 'current_field'])

    if not [model_name or current_field or instance_data]:
        return await message.edit_text('Aloqa darchasi eskirgan yoki kutilmagan xatolik!')
    
    instance = await hydrate_instance_from_data(model_name, instance_data, session)

    rel_objects = getattr(instance, current_field, [])
    ids = [obj.id for obj in rel_objects] if isinstance(rel_objects, list) else [rel_objects.id] if rel_objects else []
    return ids
