import numpy as np
from PIL import Image
from opengl_gui.gui_helper import rasterize_svg

class Icons():
    def __init__(self, icon_width, icon_height, demos):
            
        self.point_icon = rasterize_svg(path = "./res/icons/hand-pointer.svg",         width = icon_width*0.7, height = icon_height*0.7)
        self.pause_icon = rasterize_svg(path = "./res/icons/pause-circle-regular.svg", width = icon_width*0.7, height = icon_height*0.7)
        self.play_icon  = rasterize_svg(path = "./res/icons/play-circle-regular.svg",  width = icon_width*0.7, height = icon_height*0.7)
        self.video_icon = rasterize_svg(path = "./res/icons/video-solid.svg", width = icon_width*1.0, height = icon_height*1.0)
        
        self.demos = {}
        for d in demos:
            icon_path = demos[d]["cfg"]["icon"]
            if icon_path.endswith(".svg"):
                self.demos[d] = rasterize_svg(
                    path = icon_path,
                    width = icon_width,
                    height = icon_height)
            elif icon_path.endswith(".png"):
                self.demos[d] = np.array(Image.open(icon_path))[:,:,3].astype(np.uint8)
            else:
                raise ValueError(f"Icon format not supported: {icon_path}")