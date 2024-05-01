from fastapi import Depends

from .context import Context


async def get_context(
    context: Context = Depends(Context.from_dependency),  # noqa: B008
) -> Context:
    return context
