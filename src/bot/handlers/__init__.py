from src.bot.handlers.debug import router as debug_router

from src.bot.handlers.MenuHandlers.MainMenuHandlers import router as main_menu_router
from src.bot.handlers.MenuHandlers.HelpHandlers import router as help_router
from src.bot.handlers.MenuHandlers.TrackingMenuHandlers import router as tracking_menu_router
from src.bot.handlers.MenuHandlers.CalculateMenuHandler import router as calculate_menu_router

from src.bot.handlers.TrackingHandlers.TrackingListHandler import router as tracking_list_router
from src.bot.handlers.TrackingHandlers.TrackingAddCarHandler import router as tracking_add_router
from src.bot.handlers.TrackingHandlers.TrackingDeleteCarHandler import router as tracking_delete_car_router
from src.bot.handlers.TrackingHandlers.TrackingStopHandler import router as tracking_stop_router
from src.bot.handlers.TrackingHandlers.TrackingStartHandler import router as tracking_start_router


from src.bot.handlers.CalculateHandlers.SetParamsHandler import router as calculate_set_fees_router
from src.bot.handlers.CalculateHandlers.CalculateCarHandler import router as calculate_car_router


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
    calculate_car_router,
    tracking_stop_router,
    tracking_start_router
)
