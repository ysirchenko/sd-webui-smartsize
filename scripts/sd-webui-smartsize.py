import modules.scripts as scripts
import gradio as gr
import os
from modules import images
from modules.processing import process_images, Processed
from modules.processing import Processed
from modules.shared import opts, cmd_opts, state
from scripts.config import Config
import contextlib
from modules.ui_components import FormRow, ToolButton
# from modules.ui_components import FormRow, FormGroup, ToolButton, FormHTML


class AspectRatioButton(ToolButton):
    def __init__(self, ar=1.0, **kwargs):
        super().__init__(**kwargs)
        self.ar = ar

    def apply(self, w, h):
        if self.ar > 1.0:
            w = self.ar * h
        elif self.ar < 1.0:
            h = w / self.ar
        else:
            min_dim = min(w, h)
            w, h = min_dim, min_dim
        return list(map(round, [w, h]))

    def reset(self, w, h):
        return [self.res, self.res]


class ResolutionButton(ToolButton):
    def __init__(self, w, h, **kwargs):
        super().__init__(**kwargs)
        self.w = w
        self.h = h

    def reset(self):
        return [self.w, self.h]


class SmartSize(scripts.Script):

    def title(self):
        return 'SmartSize'

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def btn_img_click(self, width_max, height_max, *imgs):
        width = width_max
        height = height_max
        step = Config.step
        for img in imgs:
            if img is not None:
                if isinstance(img, dict):
                    img = img['image']
                if img.size is not None:
                    width, height = img.size
                    ar = min(width_max / width, height_max / height)
                    return [int(width * ar // step) * step, int(height * ar // step) * step]
        return [width, height]

    def btn_resolution_click(self, width, height):
        return [width, height]

    def ui(self, is_img2img):
        Config.read()
        if is_img2img:
            outputs = [self.img2img_width, self.img2img_height]
        else:
            outputs = [self.txt2img_width, self.txt2img_height]
        with gr.Blocks():
            with gr.Row():
                btn_img = ToolButton(value='Img')
                aspect_ratios_buttons = [
                    AspectRatioButton(ar=aspect_ratio['value'], value=aspect_ratio['text'])
                    for aspect_ratio in Config.aspect_ratios
                ]
                with contextlib.suppress(AttributeError):
                    for button in aspect_ratios_buttons:
                        button.click(
                            button.apply,
                            inputs=outputs,
                            outputs=outputs,
                        )
                resolutions_buttons = [
                    ResolutionButton(w=resolution['width'], h=resolution['height'], value=resolution['text'])
                    for resolution in Config.resolutions
                ]
                with contextlib.suppress(AttributeError):
                    for button in resolutions_buttons:
                        button.click(
                            button.reset,
                            outputs=outputs,
                        )
                width_max_slider = gr.Number(label='Width(max)', value=Config.width_max, elem_id='width_max_slider')
                height_max_slider = gr.Number(label='Height(max)', value=Config.height_max, elem_id='height_max_slider')
                if is_img2img:
                    btn_img.click(self.btn_img_click,
                                  inputs=[width_max_slider, height_max_slider,
                                          self.img2img_image, self.img2img_sketch, self.img2maskimg,
                                          self.inpaint_sketch],
                                  outputs=outputs)
                else:
                    btn_img.click(self.btn_img_click,
                                  inputs=[width_max_slider, height_max_slider],
                                  outputs=outputs)

    def after_component(self, component, **kwargs):
        if kwargs.get('elem_id') == 'img2img_image':
            self.img2img_image = component
        if kwargs.get('elem_id') == 'img2img_sketch':
            self.img2img_sketch = component
        if kwargs.get('elem_id') == 'img2maskimg':
            self.img2maskimg = component
        if kwargs.get('elem_id') == 'inpaint_sketch':
            self.inpaint_sketch = component
        if kwargs.get('elem_id') == 'txt2img_width':
            self.txt2img_width = component
        if kwargs.get('elem_id') == 'txt2img_height':
            self.txt2img_height = component
        if kwargs.get('elem_id') == 'img2img_width':
            self.img2img_width = component
        if kwargs.get('elem_id') == 'img2img_height':
            self.img2img_height = component
