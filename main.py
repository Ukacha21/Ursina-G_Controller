from ursina import *
from gun_controller import Gun_Controller
from ursina.prefabs.first_person_controller import FirstPersonController as FPC
# import random
from ursina.shaders import basic_lighting_shader

root = Ursina()
root.shader = basic_lighting_shader  # Optional for lighting effects
        
gun_model = "models/submachine-gun/Tec_9.fbx"
gun_texture = "models/submachine-gun/Tec_9_low_lambert1_Roughness.jpg"
Audio("audio/loop.mp3")

terrain = Entity(
model="quad",
texture="grass",
color=color.violet,
scale=(400, 400, 15),
collider="box",
rotation_x=90,
position=(0, -5, 0),
double_sided=True
)
stand_pos = Entity(
    model="cube",
    texture="brick",
    color=color.orange,
    scale=3,
    collider="box",
    position=(0, -5, 5),
    double_sided=True
    )
player = FPC()
gun = Gun_Controller(gun_model, player, gun_texture, stand_pos)


root.run()
