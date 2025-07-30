from src.bot.handlers.debug import router as debug_router
from src.bot.handlers.main_menu_handlers import router as main_menu_router
from src.bot.handlers.help_handlers import router as help_router
from src.bot.handlers.tracking_menu_handlers import (
    router as tracking_menu_router,
)
from src.bot.handlers.tracking_handlers.trakicng_list_handler import (
    router as tracking_list_router,
)
from src.bot.handlers.tracking_handlers.tracking_add_car_handler import (
    router as tracking_add_router,
)
from src.bot.handlers.tracking_handlers.tracking_delete_car_handler import (
    router as tracking_delete_car_router,
)
from src.bot.handlers.calculate_handler import (
    router as calculate_menu_router,
)
from src.bot.handlers.calculate_handlers.set_params_handler import (
    router as calculate_set_fees_router,
)


all_routers = (
    debug_router,
    main_menu_router,
    help_router,
    tracking_menu_router,
    tracking_list_router,
    tracking_add_router,
    tracking_delete_car_router,
    calculate_menu_router,
    calculate_set_fees_router,
)
