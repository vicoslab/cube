import glfw

from opengl_gui.gui_components import *
from opengl_gui.gui_helper     import *

from gui_echolib import EcholibHandler

from gui_components import Colours, setup_drawer_close_animation, State
from gui_parts.calibration_menu import create_calibration_menu
from gui_parts.demo_buttons import create_demo_buttons
from gui_parts.demo_scene import demo_scene_wrapper, demo_video_scene
from gui_parts.header_bar import create_header
from gui_parts.icons import Icons
from gui_parts.hint import create_hint
from gui_parts.intro_video import create_intro_video
from gui_parts.extend_interaction import ExtendedGui
from load_demos import load_demos

import configparser

def apply_demo_config(key: str, state: State):
    '''
    Apply saved camera settings for demo, if they exist
    '''
    cfg = state.config
    entry = f"demos.{key}"
    if entry in cfg:
        cfg = cfg[entry]
        if "balance_ratio" in cfg:
            val = cfg["balance_ratio"]
            state.echolib_handler.append_camera_command(f'BalanceRatio {val}')
            state.echolib_handler.docker_camera_properties["BalanceRatio"] = [val]
        if "exposure_time" in cfg:
            val = cfg["exposure_time"]
            state.echolib_handler.append_camera_command(f'ExposureTime {val}')
            state.echolib_handler.docker_camera_properties["ExposureTime"] = [val]

def start_container(state: State, demos, id):
    '''
    Start container of demo ``id`` and set it as active
    '''
    docker_command = "{} {}".format(1, demos[id]["cfg"]["dockerId"])
    state.echolib_handler.append_command((state.echolib_handler.docker_publisher, docker_command))
    state.active_demo = id
    
def stop_container(state: State, demos, id):
    '''
    Stop container of demo ``id`` and set it as active
    '''
    if state.echolib_handler.docker_channel_out is not None:
        # stop processing
        state.echolib_handler.append_command((state.echolib_handler.docker_channel_out, 0))
    docker_command = "{} {}".format(-1, demos[id]["cfg"]["dockerId"])
    state.echolib_handler.append_command((state.echolib_handler.docker_publisher, docker_command))
    state.active_demo = None

def scene_primary(window_width: int, window_height: int, state: State, font: dict) -> Element:
    aspect_ratio = window_width / window_height
    icon_width  = int(window_width*0.1)
    icon_height = int(window_height*0.1)

    #
    # Load Demos
    #
    demos = load_demos()
    demo_videos = {}

    for d in demos:
        video = Video(path = demos[d]["cfg"]["video"], loop = True)
        demo_videos[d] = video

    icons = Icons(icon_width, icon_height, demos)

    #
    # Main Menu
    #
    display_screen = DemoDisplay(
        position = [0.0, 0.0],
        scale  = [1.0, 1.0],
        depth  = 0.99,
        colour = Colours.WHITE,
        id = "base_display_screen")

    vicos_intro_video, vicos_intro_texture = create_intro_video()
    display_screen.insert_default(element = vicos_intro_texture)
    vicos_intro_video.play()

    hint = create_hint(icons, aspect_ratio)
    hint.depends_on(element = display_screen)
    #
    # Header bar
    #
    header_height = 0.05
    header_bar = create_header(state, demos, header_height, aspect_ratio, font)
    header_bar.depends_on(element = display_screen)
    header_bar.set_depth(depth = display_screen.properties[0] - 0.02)

    #
    # Sidebar
    #
    def on_close(element, gui):
        if display_screen.active_video is None and display_screen.active_demo is None:
            hint.position[0] = 0.87
            hint.animation_play(animation_to_play = "fade_in")

    def on_grab(element, gui):
        hint.animation_play(animation_to_play = "fade_out")

    drawer_menu = DrawerMenu(
        position = [0.93, header_height],
        scale    = [1.0, 1.0 - header_height],
        position_opened = [0.65, header_height],
        position_closed = [0.93, header_height],
        id = "drawer_menu",
        on_grab = on_grab,
        on_close = on_close)
    drawer_menu_container = Container(
        position = [0.0, 0.0],
        scale = [0.35, 1.0 - header_height],
        colour = Colours.VICOS_RED,
        id = "drawer_menu_container")

    setup_drawer_close_animation(drawer_menu, drawer_menu_container, "close")
    drawer_menu_container.depends_on(element = drawer_menu)

    #
    # Calibration menu
    #
    def calibration_on_grab(component, gui: Gui):

        if len(component.dependent_components[0].dependent_components) > 0:
            return

        if drawer_menu.open:
            drawer_menu_container.animation_play("close")

        for c in create_calibration_menu(state, font, aspect_ratio):
            c.depends_on(element = component.dependent_components[0])
            c.update_geometry(parent = component.dependent_components[0])

    def calibration_on_open(component, gui: Gui):
        gui.grab_interaction_context(component)

    def calibration_on_close(component, gui: Gui):
        gui.release_interaction_context(component)
        component.dependent_components[0].dependent_components.clear()

    drawer_menu_calibration = DrawerMenu(
        position = [0.0, 0.9],
        scale    = [1.0, 1.0 + header_height],
        position_opened = [0.0,-header_height],
        position_closed = [0.0, 0.9],
        id = "drawer_menu_calibration",
        on_open = calibration_on_open,
        on_grab  = calibration_on_grab,
        on_close = calibration_on_close)
    drawer_menu_calibration_container = Container(
        position = [0.0, 0.0],
        offset   = [0.0, 0.2],
        scale    = [1.0, 1.0],
        colour = Colours.VICOS_GRAY_NON_TRANSPARENT,
        id = "drawer_meanu_calibrated_container")
    
    drawer_menu_calibration_container.depends_on(element = drawer_menu_calibration)

    # Calibration drawer is going to be drawn over hint
    # and over the demo drawer menu
    drawer_menu.depends_on(element = display_screen)
    drawer_menu_calibration.depends_on(element = display_screen)

    parameters = Parameters(
        font   = font,
        aspect = aspect_ratio,
        state  = state)

    def on_click_video_button(button: Button, gui: Gui, state: State):

        video_key = button.id
        button.animation_play(animation_to_play = "scale_up")

        if display_screen.active_video is None:
            display_screen.insert_active_video(active_video = demo_video_scene(icons, aspect_ratio, demo_videos[video_key]), active_video_button = button)

            button.set_colour(colour = Colours.VICOS_GRAY)
        else:
            if button.mouse_click_count % 2 == 0:
                display_screen.remove_active_video()

                button.set_colour(colour = Colours.VICOS_RED)
            else:
                display_screen.active_video_button.mouse_click_count += 1
                display_screen.active_video_button.set_colour(colour = Colours.VICOS_RED)

                display_screen.insert_active_video(active_video = demo_video_scene(icons, aspect_ratio, demo_videos[video_key]), active_video_button = button)

                button.set_colour(colour = Colours.VICOS_GRAY)
        # TODO: it may not be best to close drawer when starting to play video, since video can only exist by clicking on drawer video button
        #close_drawer()
        
    def on_click_demo_button(button: Button, gui: Gui, state: State):
        
        demo_key = button.id
        button.animation_play(animation_to_play = "scale_up")

        if state.active_demo is None:
            start_container(state, demos, demo_key)
            apply_demo_config(demo_key, state)
            
            display_screen.insert_active_demo(active_demo = demo_scene_wrapper(aspect_ratio, demos[demo_key]["get_scene"](parameters), state.get_aspect_ratio()), active_demo_button = button)

            button.set_colour(colour = Colours.VICOS_GRAY)
            vicos_intro_texture.animation_play(animation_to_play = "fade_out")
            hint.animation_play(animation_to_play = "fade_out")
            state.status = demos[demo_key]["cfg"][f"highlight-{state.language}"]
        else:
            if button.mouse_click_count % 2 == 0:
                display_screen.remove_active_demo()

                stop_container(state, demos, demo_key)

                button.set_colour(colour = Colours.VICOS_RED)
                vicos_intro_texture.animation_play(animation_to_play = "fade_in")
                hint.animation_play(animation_to_play = "fade_in")
                state.status = None
            else:
                display_screen.active_demo_button.mouse_click_count += 1
                display_screen.active_demo_button.set_colour(colour = Colours.VICOS_RED)

                stop_container(state, demos, state.active_demo)
                start_container(state, demos, demo_key)
                apply_demo_config(demo_key, state)

                display_screen.insert_active_demo(active_demo = demo_scene_wrapper(aspect_ratio, demos[demo_key]["get_scene"](parameters), state.get_aspect_ratio()), active_demo_button = button)

                button.set_colour(colour = Colours.VICOS_GRAY)
                state.status = demos[demo_key]["cfg"][f"highlight-{state.language}"]

        state.echolib_handler.docker_channel_ready = False # Reset image return after demo is switched or terminated
        
        if drawer_menu.open:
            drawer_menu_container.animation_play(animation_to_play = "close")
        
    #### Construct demos ####

    demo_buttons_position = 0.05
    for id in demos.keys():
        button_main, button_video = create_demo_buttons(icons, demos, id, demo_buttons_position, aspect_ratio, font)

        demo_buttons_position += 0.1
        
        button_main.on_click = on_click_demo_button
        button_main.depends_on(element = drawer_menu_container)

        button_video.on_click = on_click_video_button
        button_video.depends_on(element = drawer_menu_container)

    return display_screen

def main():

    print("Starting VICOS DEMO OpenGL")

    config = configparser.ConfigParser()
    CONFIG = 'config.ini'
    config.read(CONFIG)
    
    WIDTH = int(config["main"]["width"])
    HEIGHT = int(config["main"]["height"])
    FULLSCREEN = config["main"]["fullscreen"].lower() == "yes"

    #######################################################

    state = State(config, EcholibHandler())

    gui = ExtendedGui(fullscreen = FULLSCREEN, width = WIDTH, height = HEIGHT)

    font = load_font(path = "./res/fonts/Metropolis-SemiBold.otf")

    scene = scene_primary(gui.width, gui.height, state, font)
    scene.update_geometry(parent = None)

    while not gui.should_window_close():

        gui.poll_events()
        gui.clear_screen()

        scene.execute(parent = None, gui = gui, custom_data = state)
        
        gui.swap_buffers()

        # Resets camera image so no unecessary re-renders are done
        state.echolib_handler.set_camera_to_none()

        if gui.should_window_resize():
            config["main"]["width"] = str(gui.width)
            config["main"]["height"] = str(gui.height)
            state.active_demo = None
            scene = scene_primary(gui.width, gui.height, state, font)
            scene.update_geometry(parent = None)

    with open(CONFIG, 'w') as configfile:
        config.write(configfile)

    state.active_demo = None
    state.echolib_handler.running = False
    state.echolib_handler.handler_thread.join()

    glUseProgram(0)
    glfw.terminate()

if __name__ == "__main__":
    main()
