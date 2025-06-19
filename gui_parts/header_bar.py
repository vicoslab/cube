from opengl_gui.gui_components import *
from gui_components import Colours, Language, State

header_bar_demo_text_default = {
    Language.SL.value: "DEMO celica",
    Language.EN.value: "DEMO booth"
}

def create_header(state, demos, header_height, aspect_ratio, font):
    '''
    Create header bar with status text and language toggle
    '''
    language_button_width = 0.05
    
    header_bar = Container(
        position = [0.0, 0.0],
        scale  = [1.0, header_height],
        depth  = 0.97,
        colour = Colours.VICOS_RED,
        id = "header_bar")
    header_bar_demo_text = TextField(
        position = [0.01, None],
        text_scale = 0.7,
        colour = [1.0, 1.0, 1.0, 0.75],
        aspect_ratio = aspect_ratio, 
        id = f"header_text_demo_name")
    
    header_bar_demo_text.status = None
    header_bar_demo_text.set_text(font = font, text = header_bar_demo_text_default[state.language])
    header_bar_demo_text.center_y()
        
    def check_status(parent: Element, gui: Gui, custom_data: State):
        state = custom_data
        if header_bar_demo_text.status != state.status:
            header_bar_demo_text.status = state.status
            header_bar_demo_text.set_text(font = font, text = state.status or header_bar_demo_text_default[state.language])
    
    header_bar_demo_text.command_chain.insert(0, check_status)
    header_bar_demo_text.depends_on(element = header_bar)
    
    def get_language_callback(lang: str):
        def on_click(button: Button, gui: Gui, state: State):
            language_buttons[state.language].set_colour(Colours.VICOS_RED)
            state.language = lang
            button.set_colour(Colours.VICOS_GRAY)
            if state.active_demo is None:
                state.status = header_bar_demo_text_default[lang]
            else:
                state.status = demos[state.active_demo]["cfg"][f"highlight-{state.language}"]
        return on_click
    
    def create_language_button(x_pos: int, lang: str):
        button = Button(
            position = [x_pos, 0],
            offset = [0.0, 0],
            scale = [language_button_width, header_height],
            colour = Colours.VICOS_RED,
            on_click = get_language_callback(lang),
            id = f"button_language_{lang}")
        button_text = TextField(
            position = None,
            text_scale = 0.7,
            colour = [1.0, 1.0, 1.0, 0.75],
            aspect_ratio = aspect_ratio, 
            id = f"button_language_text_{lang}")
        button_text.depends_on(button)
        button_text.set_text(font = font, text = lang.upper())
        button_text.center_x()
        button_text.center_y()
        return button

    language_buttons = {}
    x_pos = 1.0
    for lang in [lang.value for lang in Language]:
        x_pos -= language_button_width
        button = create_language_button(x_pos, lang)
        button.depends_on(element = header_bar)
        if lang == state.language: # default language
            button.set_colour(Colours.VICOS_GRAY)
        language_buttons[lang] = button
    return header_bar