from opengl_gui.gui_components import *

def create_intro_video():
    vicos_intro_video = Video(path = "./res/vicos.mp4", loop = False)

    intro_fade_out = AnimationListOne(
        transform = ("properties", 0.25),
        duration  = 0.5,
        index = 1,
        id = "fade_out")
    
    intro_fade_in = AnimationListOne(
        transform = ("properties", 1.0),
        duration  = 0.5,
        index = 1,
        id = "fade_in")

    vicos_intro_texture = TextureRGB(
        position = [0.0, 0.0],
        scale    = [1.0, 1.0],
        depth = 0.98,
        alpha = 1.0,
        animations = {intro_fade_out.id: intro_fade_out, intro_fade_in.id: intro_fade_in},
        id = "vicos_intro_texutre",
        get_texture = lambda g, cd: vicos_intro_video.get_frame(),
        set_once = False)

    return vicos_intro_video, vicos_intro_texture