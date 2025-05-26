from opengl_gui.gui_components import *
from gui_parts.icons import Icons
from gui_components import Colours

def create_hint(icons: Icons, aspect_ratio):
    point_icon = icons.point_icon
    point_icon_aspect_ratio = point_icon.shape[1]/point_icon.shape[0]

    x = 0.87
    y = 0.4755

    fade_in = AnimationListOne(
        transform = ("colour", 0.75),
        on_end    = lambda c, g, u: c.animation_play(animation_to_play = "move_0"),
        duration  = 0.25,
        id = "fade_in",
        index = 3)

    fade_out = AnimationListOne(
        transform = ("colour", 0.0),
        duration  = 0.25,
        id = "fade_out",
        index = 3)

    move_0 = AnimationList(
        transform = ("position", [x - 0.02, y]),
        on_end    = lambda c, g, u: c.animation_play(animation_to_play = "move_1"),
        duration  = 0.75,
        id = "move_0")

    move_1 = AnimationList(
        transform = ("position", [x, y]),
        on_end    = lambda c, g, u: c.animation_play(animation_to_play = "move_0"),
        duration  = 0.75,
        id = "move_1")

    pointer_texture = TextureR(
        position = [x, y],
        scale  = [point_icon_aspect_ratio*0.07/aspect_ratio, 0.07],
        depth  = 0.98,
        colour = Colours.VICOS_RED,
        animations = {fade_in.id: fade_in, fade_out.id: fade_out, move_0.id: move_0, move_1.id: move_1},
        id = "hint",
        get_texture = lambda g, cd: point_icon,
        set_once = True)

    pointer_texture.animation_play(animation_to_play = "fade_in")

    return pointer_texture
