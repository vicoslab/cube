from gui_components import Language, TextFieldMultilingual, Colours, SettableRangeSlider, State, Toggle
from opengl_gui.gui_components import Container, Gui, DisplayTexture, Button, RangeSlider
import time
import numpy as np

calibration_title_content = {
    Language.EN: "Camera calibration",
    Language.SL: "Kalibracija kamere"
}
label_advanced_mode = {
    Language.EN: "Per-demo config",
    Language.SL: "Za vsak demo ločeno"
}
d_original_content = {
    Language.EN: "Original size",
    Language.SL: "Originalna velikost"
}
d_zoom_content = {
    Language.EN: "Enlarged size",
    Language.SL: "Povečana velikost"
}
ax_text_content = {
    Language.EN: "Automatic exposure",
    Language.SL: "Samodejna osvetlitev"
}
awb_text_content = {
    Language.EN: "Automatic  balance",
    Language.SL: "Samodejna raven beline"
}
slider_awb_text_content = {
    Language.EN: "White balance: {:.2f}",
    Language.SL: "Raven beline: {:.2f}"
}
slider_ax_text_content = {
    Language.EN: "Exposure time: {:.3f} ms",
    Language.SL: "Čas osvetlitve: {:.3f} ms"
}

def create_calibration_menu(state: State, font, aspect_ratio):

    def calibration_title_language_callback(field, lang):
        field.set_text(font = font, text = calibration_title_content[lang])
        field.center_x()
    calibration_title = TextFieldMultilingual(
        position = [0.05, 0.05],
        text_scale = 0.68,
        colour = [1.0, 1.0, 1.0, 0.75],
        aspect_ratio = aspect_ratio,
        id = "calibration_title",
        language_callback = calibration_title_language_callback)

    advanced_mode = TextFieldMultilingual(
        position = [0.75, 0.05],
        text_scale = 0.68,
        colour = [0.8, 0.8, 0.8, 0.75],
        aspect_ratio = aspect_ratio,
        id = "advanced_mode",
        language_callback = lambda field, lang: field.set_text(font = font, text = label_advanced_mode[lang]))
    def advanced_mode_on_click(button, gui, custom_data):
        if button.mouse_click_count % 2 == 0:
            custom_data.advanced_mode = False
        else:
            custom_data.advanced_mode = True
    advanced_mode_toggle = Toggle(
        position = [0.95, 0.02],
        id = "advanced_mode_toggle",
        scale = [0.04, 0.04],
        initial_state = int(state.advanced_mode),
        aspect_ratio = aspect_ratio,
        on_click = advanced_mode_on_click
    )

    # Create live feed component

    def get_original(gui: Gui, state: State):
        return state.echolib_handler.get_camera_stream()

    def get_zoom(gui: Gui, state: State):

        zoom_margin_y = 400
        zoom_margin_x = np.int32(np.floor(zoom_margin_y/state.get_aspect_ratio()))

        image = state.echolib_handler.get_camera_stream()

        if image is None:
            return None

        return image[zoom_margin_x:-zoom_margin_x, zoom_margin_y:-zoom_margin_y, :]

    def get_display(position, scale, title, get_texture, id):

        calibration_live_feed_container = Container(
            position = position,
            scale    = [scale/state.get_aspect_ratio(), scale],
            colour = [1.0, 1.0, 1.0, 0.8],
            id = f"calibration_display_container_ {id}") 

        calibration_display_live_feed = DisplayTexture(
            position = [0.1, 0.07],
            scale    = [(scale - 0.01)/state.get_aspect_ratio(), scale - 0.05],
            aspect = state.get_aspect_ratio(),
            id = f"calibration_display_{id}",
            get_texture = get_texture)

        def calibration_live_feed_title_language_callback(field, lang):
            field.set_text(font = font, text = title[lang])
            field.center_x()
            
        calibration_live_feed_title = TextFieldMultilingual(
                position = [0.05, 0.05],
                text_scale = 0.7,
                colour = [0.0, 0.0, 0.0, 0.75],
                aspect_ratio = aspect_ratio, 
                id = f"calibration_display_title_{id}",
                language_callback=calibration_live_feed_title_language_callback)

        calibration_live_feed_title.depends_on(element = calibration_live_feed_container)
        calibration_display_live_feed.center_x()

        calibration_display_live_feed.depends_on(element = calibration_live_feed_container)

        return calibration_live_feed_container

    d_original = get_display(position = [0.025, 0.28], scale = 0.62, title = d_original_content, get_texture = get_original, id = 0)
    d_zoom     = get_display(position = [0.51,  0.28], scale = 0.62, title = d_zoom_content,   get_texture = get_zoom, id = 1)

    button_container = Container(
        position = [0.01, 0.08],
        scale  = [1.0, 0.2],
        depth  = 0.97,
        colour = [1.0, 1.0, 1.0, 0.5],
        id = "button_contianer")

    button_container.command_chain.pop(1)

    button_awb = Button(
        position = [0.025, 0.04],
        offset = [0.0, 0.015*aspect_ratio],
        scale  = [0.22, 0.09],
        colour = Colours.VICOS_RED,
        id = "button_awb")

    def awb_text_language_callback(field, lang):
        field.set_text(font = font, text = awb_text_content[lang])
        field.center_x()
        field.center_y()
    button_awb_text = TextFieldMultilingual(
        position = [0.0, 0.0],
        text_scale = 0.68,
        colour = [1.0, 1.0, 1.0, 0.75],
        aspect_ratio = aspect_ratio, 
        id = "button_awb_text",
        language_callback=awb_text_language_callback)

    button_awb_text.depends_on(element = button_awb)

    button_ax = Button(
        position = [0.275, 0.04],
        offset = [0.0, 0.015*aspect_ratio],
        scale  = [0.22, 0.09],
        colour = Colours.VICOS_RED,
        id = "button_ax")

    def ax_text_language_callback(field, lang):
        field.set_text(font = font, text = ax_text_content[lang])
        field.center_x()
        field.center_y()
    button_ax_text = TextFieldMultilingual(
        position = [0.0, 0.0],
        text_scale = 0.68,
        colour = [1.0, 1.0, 1.0, 0.75],
        aspect_ratio = aspect_ratio, 
        id = "button_ax_text",
        language_callback=ax_text_language_callback)

    button_ax_text.depends_on(element = button_ax)

    def slider_awb_get_range(slider: RangeSlider, state):
        properties = state.echolib_handler.docker_camera_properties

        if "BalanceRatioRange" not in properties:
            return None

        lower, upper = map(float, properties["BalanceRatioRange"])
        return lower, upper

    def slider_ax_get_range(slider: RangeSlider, state):
        properties = state.echolib_handler.docker_camera_properties
        
        if "ExposureTimeRange" not in properties:
            return None
        
        lower, upper = map(float, properties["ExposureTimeRange"])
        # Limit upper for slider accuracy
        return lower, min(upper, 39062.3407109375)

    slider_awb = SettableRangeSlider(
        position = [0.58, 0.04],
        scale = [0.15, 0.01],
        aspect_ratio = aspect_ratio,
        get_range = slider_awb_get_range,
        id = "range_slider_awb")

    camera_properties = state.echolib_handler.docker_camera_properties
    range = slider_awb_get_range(slider_awb, state)
    if "BalanceRatio" in camera_properties and range is not None:
            slider_awb.range_bottom, slider_awb.range_top = range
            slider_awb.set_value(float(camera_properties["BalanceRatio"][0]))

    slider_ax = SettableRangeSlider(
        position = [0.78, 0.04],
        scale = [0.15, 0.01],
        aspect_ratio = aspect_ratio,
        get_range = slider_ax_get_range,
        id = "range_slider_ax")

    range = slider_ax_get_range(slider_ax, state)
    if "ExposureTime" in camera_properties and range is not None:
            slider_ax.range_bottom, slider_ax.range_top = range
            slider_ax.set_value(float(camera_properties["ExposureTime"][0]))

    def slider_awb_text_language_callback(field, lang):
        field.set_text(font = font, text = slider_awb_text_content[lang].format(slider_awb.selected_value))
    slider_awb_text = TextFieldMultilingual(
        position = [0.575, 0.3],
        text_scale = 0.68,
        colour = [1.0, 1.0, 1.0, 0.75],
        aspect_ratio = aspect_ratio, 
        id = "slider_awb_text",
        language_callback=slider_awb_text_language_callback)

    def slider_ax_text_language_callback(field, lang):
        field.set_text(font = font, text = slider_ax_text_content[lang].format(slider_ax.selected_value*1e-6))
    slider_ax_text = TextFieldMultilingual(
        position = [0.76, 0.3],
        text_scale = 0.68,
        colour = [1.0, 1.0, 1.0, 0.75],
        aspect_ratio = aspect_ratio, 
        id = "slider_ax_text",
        language_callback=slider_ax_text_language_callback)

    slider_awb.on_value_update  = lambda slider, state: slider_awb_text_language_callback(slider_awb_text, state.language)
    slider_ax.on_value_update  = lambda slider, state: slider_ax_text_language_callback(slider_ax_text, state.language)

    def slider_awb_on_select(slider: RangeSlider, state):
        state.echolib_handler.append_camera_command(f"BalanceRatio {slider.selected_value}")
        state.echolib_handler.docker_camera_properties["BalanceRatio"] = [slider.selected_value]
        if state.active_demo is not None:
            section = f"demos.{state.active_demo}"
            if section not in state.config:
                state.config[section] = {}
            state.config[section]["balance_ratio"] = str(slider.selected_value)

    def slider_ax_on_select(slider: RangeSlider, state):
        state.echolib_handler.append_camera_command(f"ExposureTime {slider.selected_value}")
        state.echolib_handler.docker_camera_properties["ExposureTime"] = [slider.selected_value]
        if state.active_demo is not None:
            section = f"demos.{state.active_demo}"
            if section not in state.config:
                state.config[section] = {}
            state.config[section]["exposure_time"] = str(slider.selected_value)

    slider_awb.on_select = slider_awb_on_select
    slider_ax.on_select = slider_ax_on_select

    def button_awb_on_click(button: Button, gui: Gui, state):
        
        if button.mouse_click_count % 2:

            slider_awb.lock()
            button.set_colour(Colours.VICOS_GRAY)

            state.echolib_handler.append_camera_command(f"BalanceWhiteAuto Once")
        else:

            slider_awb.unlock()
            button.set_colour(Colours.VICOS_RED)

            state.echolib_handler.append_camera_command(f"BalanceWhiteAuto Off")
            state.echolib_handler.append_camera_command(f"GetBalanceRatio _")
            time.sleep(1.5)

            if "BalanceRatio" in camera_properties:
                slider_awb.set_value(float(camera_properties["BalanceRatio"][0]))
                slider_awb_text.language_callback(slider_awb_text, slider_awb_text.language) # trigger text update

            if state.active_demo is not None:
                section = f"demos.{state.active_demo}"
                if section not in state.config:
                    state.config[section] = {}
                state.config[section]["balance_ratio"] = \
                    str(state.echolib_handler.docker_camera_properties["BalanceRatio"][0])
            

    def button_ax_on_click(button: Button, gui: Gui, state):

        if button.mouse_click_count % 2:

            slider_ax.lock()
            button.set_colour(Colours.VICOS_GRAY)

            state.echolib_handler.append_camera_command(f"ExposureAuto Once")
        else:

            slider_ax.unlock()
            button.set_colour(Colours.VICOS_RED)

            state.echolib_handler.append_camera_command(f"ExposureAuto Off")
            state.echolib_handler.append_camera_command(f"GetExposureTime _")
            time.sleep(1.5)

            if "ExposureTime" in camera_properties:
                slider_ax.set_value(float(camera_properties["ExposureTime"][0]))
                slider_ax_text.language_callback(slider_ax_text, slider_ax_text.language) # trigger text update

            if state.active_demo is not None:
                section = f"demos.{state.active_demo}"
                if section not in state.config:
                    state.config[section] = {}
                state.config[section]["balance_ratio"] = \
                    str(state.echolib_handler.docker_camera_properties["BalanceRatio"][0])

    button_awb.on_click = button_awb_on_click
    button_ax.on_click  = button_ax_on_click

    button_awb.center_y()
    button_ax.center_y()
    slider_awb.center_y()
    slider_ax.center_y()

    button_awb.depends_on(element = button_container)
    button_ax.depends_on(element  = button_container)
    slider_awb.depends_on(element = button_container)
    slider_ax.depends_on(element  = button_container)
    slider_awb_text.depends_on(element = button_container)
    slider_ax_text.depends_on(element = button_container)

    return [d_original, d_zoom, calibration_title, advanced_mode, advanced_mode_toggle, button_container]
