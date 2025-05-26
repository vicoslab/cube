from threading import Thread, Lock
import numpy as np

from opengl_gui.gui_components import *
from gui_components import State
from gui_parts.icons import Icons

def demo_scene_wrapper(window_aspect_ratio: float, demo_component: dict, camera_aspect_ratio: float = 4024.0/3036.0) -> DisplayTexture:

    in_animation = AnimationList(
        transform = ("position", [0.5, 0.0]),
        duration  = 0.75,
        id = "in")

    out_animation = AnimationList(
        transform = ("position", [-2.0, 0.0]),
        duration  = 0.75,
        id = "out")

    display = DisplayTexture(
        position = [2.0, 0.0],
        scale    = [1.0/camera_aspect_ratio, 1.0],
        depth  = 0.95,
        aspect = camera_aspect_ratio,
        animations = {in_animation.id: in_animation, out_animation.id: out_animation},
        id = "demo_display_texture",
        get_texture = demo_component["get_docker_texture"])

    if "worker" in demo_component:
        Thread(target=demo_component["worker"]).start()

    for c in demo_component["elements"]:
        c.depends_on(element = display)

    display.offset[0] = -1.0/camera_aspect_ratio

    return display

def demo_video_scene(icons: Icons, aspect_ratio: float, video: Video) -> Element:

    play_aspect  = icons.play_icon.shape[1]/icons.play_icon.shape[0]

    play_texture = TextureR(
        position = [0.0, 0.0],
        scale  = [play_aspect*0.085/aspect_ratio, 0.085],
        colour = [1.0, 1.0, 1.0, 1.0],
        id = "play_texture_video",
        get_texture = lambda g, cd: icons.play_icon,
        set_once    = True)

    pause_texture = TextureR(
        position = [0.0, 0.0],
        scale = [play_aspect*0.085/aspect_ratio, 0.085],
        colour = [1.0, 1.0, 1.0, 1.0],
        id = "pause_texture_video",
        get_texture = lambda g, cd: icons.pause_icon,
        set_once    = True)

    def on_click(button: Button, gui: Gui, state: State):

        button.dependent_components.clear()

        if button.mouse_click_count % 2 == 0:

            pause_texture.depends_on(element = button)
            pause_texture.center_x()
            pause_texture.center_y()

            video.resume()
        else:

            play_texture.depends_on(element = button)
            play_texture.center_x()
            play_texture.center_y()

            play_texture.update_geometry(parent = button)

            video.pause()

        print(f"Clicking on button: {button.id}")

    ina = AnimationList(
        transform = ("position", [0.0, 0.0]),
        duration  = 0.75,
        id = "in")

    outa = AnimationList(
        transform = ("position", [-2.0, 0.0]),
        duration  = 0.75,
        id = "out")

    button_in = AnimationList(
        transform = ("position", [None, 0.9]),
        duration  = 1.0,
        id = "button_in")

    button_pause_play = Button(
        colour   = [226.0/255, 61.0/255, 40.0/255.0, 1.0],
        position = [0.2, 2.0],
        scale      = [0.08/aspect_ratio, 0.08],
        on_click   = on_click,
        animations = {button_in.id: button_in},
        shader = "circle_shader",
        id     = "video_button_play_pause")

    pause_texture.depends_on(element = button_pause_play)
    pause_texture.center_x()
    pause_texture.center_y()

    display = DisplayTexture(
        position = [0.0, 0.0],
        scale = [1.0, 1.0],
        get_texture = lambda g, cd: video.get_frame(),
        animations = {ina.id: ina, outa.id: outa},
        id = "traffic_display")

    button_pause_play.depends_on(element = display)
    button_pause_play.center_x()
    button_pause_play.animation_play(animation_to_play = "button_in")

    video.reset_and_play()

    return display
