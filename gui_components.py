from enum import Enum
from opengl_gui.gui_components import TextField, RangeSlider, Container, DrawerMenu, AnimationList, AnimationScalar, Gui
import numpy as np

class Colours():
    WHITE = [1.0, 1.0, 1.0, 1.0]
    VICOS_RED  = [226.0/255, 61.0/255, 40.0/255.0, 0.75]
    VICOS_GRAY = [85.0/255.0, 85.0/255.0, 85.0/255.0, 0.35]
    VICOS_GRAY_NON_TRANSPARENT = [85.0/255.0, 85.0/255.0, 85.0/255.0, 0.8]


class Language(str, Enum):
    EN = "en"
    SL = "sl"


class State():
    '''
    State object that gets passed around in callbacks, etc.
    '''
    def __init__(self, config, echolib_handler):

        self.echolib_handler = echolib_handler
        self.language = Language.SL
        self.config = config
        self.active_demo = None
        self.status = None

        self.default_camera_aspect_ratio = 4024.0/3036.0

    def get_aspect_ratio(self) -> float:
        return self.default_camera_aspect_ratio


class TextFieldMultilingual(TextField):
    '''
    Text field that detects language changes and requests updated value
    '''
    def __init__(self, language_callback, **kwargs):
        super(TextFieldMultilingual, self).__init__(**kwargs)

        self.language = None
        self.language_callback = language_callback
        self.command_chain.insert(0, self.update_content_language)
    
    def update_content_language(self, parent, gui, custom_data):
        if self.language != custom_data.language:
            self.language = custom_data.language
            self.language_callback(self, self.language)


slider_to_red = AnimationList(
    transform = ("colour", Colours.VICOS_RED),
    duration  = 0.2,
    id = "slider_to_red")
slider_to_white = AnimationList(
    transform = ("colour", Colours.WHITE),
    duration  = 0.2,
    id = "slider_to_white")

class SettableRangeSlider(RangeSlider):
    '''
    Range slider that supports setting values programatically.
    Also applies some custom colours/animations
    '''
    def __init__(self, **kwargs):
        if "range_bottom" not in kwargs:
            kwargs["range_bottom"] = 0.0
        if "range_top" not in kwargs:
            kwargs["range_top"] = 1.0
        if "colour" not in kwargs:
            kwargs["colour"] = Colours.VICOS_RED
        super().__init__(**kwargs)
        self.circle.animations = {slider_to_red.id: slider_to_red, slider_to_white.id: slider_to_white}
    
    def _maybe_update_range(self):
        if self.get_range is not None:
            range = self.get_range()
            if range is not None:
                self.range_bottom, self.range_top = range
    
    def set_thumb_position(self, position):
        self.circle.position[0] = np.clip(position, 0.0, 1.0)
        # element_update sets value from position, but someone might try to access this before that
        self.selected_value = self.range_bottom + self.circle.position[0]*(self.range_top - self.range_bottom)
    
    def set_value(self, value):
        self.circle.position[0] = np.clip((value - self.range_bottom)/(self.range_top - self.range_bottom), 0.0, 1.0)
        # element_update sets value from position, but someone might try to access this before that
        self.selected_value = value
        
    def lock(self):
        self.circle.animation_play(slider_to_red.id)
        super().lock()
    
    def unlock(self):
        self.circle.animation_play(slider_to_white.id)
        super().unlock()

class TouchContainer(Container):
    def __init__(self, on_press=None, on_move=None, **kwargs):
        super().__init__(**kwargs)
        self.on_press = on_press
        self.on_move = on_move
        
        def mouse_update(parent, gui: Gui, custom_data):
            
            if gui.mouse_press_event is not None:
                if self.on_press is not None:
                    is_pressed, x, y = gui.mouse_press_event
                    self.on_press(is_pressed, x, y, custom_data)

            elif self.on_move is not None:
                if gui.dx == 0 and gui.dy == 0 or self.on_move is None:
                    return
                self.on_move(gui.x_pos, gui.y_pos, custom_data)
  
        self.command_chain.insert(0, mouse_update)

    def to_local(self, x, y):
        '''
        Convert coordinates to representation relative to this element.
        (0,0) is top left, (1,1) is bottom right. None means outside
        '''
        left, top = self.top
        right, bottom = self.bot
        if x < left or x > right or y < bottom or y > top:
            return None
        x = (x - left) / (right - left)
        y = 1 - (y - bottom) / (top - bottom)
        return x,y

def setup_drawer_close_animation (drawer: DrawerMenu, drawer_container: Container, id: str):
    '''
    Assign ``drawer_container`` animation ``id`` that animates the closing of ``drawer``.
    ``drawer_container`` should be the direct child of ``drawer``.
    This is done because animating a DrawerMenu itself does not seem to work.
    '''
    # Since animations don't seem to work with drawers, we move the container
    initial_position = drawer_container.position.copy()
    x_open, y_open = drawer.position_opened
    x_closed, y_closed = drawer.position_closed
    dxy = np.array([x_closed - x_open, y_closed - y_open])

    def on_end (c, g, u):
        drawer.open = False
        drawer.on_close(None,None)
        drawer.position = drawer.position_closed.copy()
        drawer_container.position = initial_position.copy()
        drawer.update_geometry(parent = None)
        print("Drawer closed")
    drawer_container.animations[id] = AnimationScalar(
        transform = ("position", dxy),
        on_end    = on_end,
        duration  = 0.5,
        id        = id)
