from gui_components import Language
import xml.etree.ElementTree as ET
import os
from importlib import import_module

def load_demos(root: str = "./demos") -> dict:
    '''
    Scan demos directory and parse their configurations
    '''
    demos = {}
    languages = [lang.value for lang in Language]

    for demo_name in os.listdir(root):
        
        demo_root = root + "/" + demo_name
        demo_has_cfg = False
        demo_has_scene = False
        
        if not os.path.isdir(demo_root):
            continue

        for demo_files in os.listdir(demo_root):
            demo_has_cfg = demo_has_cfg or demo_files == "cfg.xml"
            demo_has_scene = demo_has_scene or demo_files == "scene.py"

        if demo_has_cfg and demo_has_scene:
            module_path = "demos." + demo_name + "." + "scene"
            module = import_module(module_path)

            attrs = [ "demoId", "dockerId", "video", "icon", "vramMin", "vramMax", "nopause" ]
            attrs_highlight = [ f"highlight-{lang}" for lang in languages ]

            xml_valid_dict = { tag: False for tag in attrs + attrs_highlight }
            xml_valid_dict["nopause"] = True # optional flag
            scene_valid = hasattr(module, "get_scene")

            xml_path = demo_root + "/cfg.xml"
            xml_tree = ET.parse(xml_path)

            xml_cfg_root = xml_tree.getroot()
            xml_parsed = {}

            if xml_cfg_root.tag == "cfg":
                for xml_c in list(xml_cfg_root): # Iterator for children
                    if xml_c.tag in [ "demoId", "dockerId" ] or \
                       xml_c.tag in attrs_highlight:
                        xml_parsed[xml_c.tag] = xml_c.text
                        xml_valid_dict[xml_c.tag] = True
                    elif xml_c.tag in [ "vramMin", "vramMax"]:
                        xml_parsed[xml_c.tag] = int(xml_c.text)
                        xml_valid_dict[xml_c.tag] = True
                    elif xml_c.tag in [ "video", "icon" ]:
                        xml_parsed[xml_c.tag] = demo_root + "/" + xml_c.text
                        xml_valid_dict[xml_c.tag] = True
                    elif xml_c.tag in [ "nopause" ]:
                        xml_parsed[xml_c.tag] = True
            xml_valid = all(xml_valid_dict.values())
                        
            if xml_valid and scene_valid:
                if xml_parsed["demoId"] in demos.keys():
                    print("Duplicated demo id -> {}".format(xml_parsed["demoId"]))
                else:
                    demos[xml_parsed["demoId"]] = {"cfg": xml_parsed, "get_scene": module.get_scene}
            else:
                if not scene_valid:
                    raise ValueError(f"Module {module_path} missing scene declaration.")
                for k,v in xml_valid_dict.items():
                    if not v:
                        raise ValueError(f"Module configuration '{module_path}/cfg.xml' is missing attribute {k}.")

    return dict(sorted(demos.items(), key = lambda x: x[1]["cfg"][f"highlight-{Language.SL.value}"]))