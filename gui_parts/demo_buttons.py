from opengl_gui.gui_components import *
from gui_components import Colours, TextFieldMultilingual
from gui_parts.icons import Icons

#### Click animation

main_scale_up = AnimationList(
    transform = ("scale", [0.265, 0.095]),
    on_end = lambda c, g, u: c.animation_play(animation_to_play = "scale_down"),
    duration  = 0.2,
    id = "scale_up")

main_scale_down = AnimationList(
    transform = ("scale", [0.26, 0.09]),
    duration  = 0.2,
    id = "scale_down")

video_scale_up = AnimationList(
    transform = ("scale", [0.075, 0.095]),
    on_end = lambda c, g, u: c.animation_play(animation_to_play = "scale_down"),
    duration  = 0.2,
    id = "scale_up")

video_scale_down = AnimationList(
    transform = ("scale", [0.07, 0.09]),
    duration  = 0.2,
    id = "scale_down")

def create_demo_buttons(icons: Icons, demos, id: str, position, aspect_ratio, font):
    video_icon = icons.video_icon
    video_icon_aspect_ratio = video_icon.shape[1]/video_icon.shape[0]
    
    video_icon_texture = TextureR(
        position = [0.0, 0.0],
        offset   = [-video_icon_aspect_ratio*0.05/aspect_ratio, 0.05],
        scale    = [ video_icon_aspect_ratio*0.05/aspect_ratio, 0.05],
        colour = Colours.WHITE,
        id = "video_icon_{}".format(id),
        get_texture = lambda g, cd: video_icon,
        set_once = True)

    button_main = Button(
        position   = [0.02, position],
        offset = [0.0, 0.015*aspect_ratio],
        scale  = [0.26, 0.09],
        depth  = 0.83,
        colour     = Colours.VICOS_RED,
        animations = { main_scale_up.id: main_scale_up, main_scale_down.id: main_scale_down },
        id = id)

    button_video = Button(
        position   = [0.78, position],
        offset = [0.0, 0.015*aspect_ratio],
        scale  = [0.07, 0.09],
        depth  = 0.83,
        colour     = Colours.VICOS_RED,
        animations = { video_scale_up.id: video_scale_up, video_scale_down.id: video_scale_down },
        id = id)

    def language_callback(field, lang):
        field.set_text(font = font, text = demos[id]["cfg"][f"highlight-{lang}"])
        field.center_y()

    button_text = TextFieldMultilingual(
        position = [0.25, position],
        offset   = [0.0, -0.022],
        text_scale = 0.7,
        depth  = 0.82,
        colour = [1.0, 1.0, 1.0, 0.75],
        aspect_ratio = aspect_ratio, 
        id = f"demo_button_text_{id}",
        language_callback=language_callback)

    demo_icon_texture = TextureR(
        position = [0.0, 0.0],
        offset = [-0.02, 0.01],
        scale    = [ 0.08, 0.08],
        colour = Colours.WHITE,
        id = f"demo_button_icon{id}",
        get_texture = lambda g, cd: icons.demos[id],
        set_once = True)

    demo_icon_texture.depends_on(element = button_main)
    button_text.depends_on(element = button_main)
    video_icon_texture.depends_on(element = button_video)
    video_icon_texture.center_x()
    video_icon_texture.center_y()
    return button_main, button_video

