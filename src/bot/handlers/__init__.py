from src.bot.handlers.debug import router as debug_router
from src.bot.handlers.main_menu_handlers import router as main_menu_router

all_routers = (
    debug_router,
    main_menu_router,
)
