"""
implementation of all gun related stuff,
aiming, shooting, bullet movement, hit detection, raycast etc
"""
from ursina import *
from ursina.shaders import basic_lighting_shader
from ursina.prefabs.first_person_controller import FirstPersonController as FPC
from threading import Timer as timer



class Gun_Controller(Entity):

    def __init__(self, gun_model, player, gun_texture, **kwargs):

        super().__init__()

        self.player = player
        self.player.gun = None
        self.gun_in_hand = False
        self.count_shoots = 0
        self.reloading = False
        # self.shots_left = 10 - self.count_shoots
        self.gun = Button(parent=scene, model=gun_model, 
            #color=color.blue,
            #scale=.02/150, #for normal first gun
            scale=.02, #for submachine gun
            texture=gun_texture,
            origin_y=-.5, 
            position=Vec3(.2,-.5,.5), 
            #collider='box', 
            )
        self.gun.on_click = self.get_gun

    def reload_gun(self):
        if self.reloading == True:
            Audio("audio/reload.mp3")
            print("reloaded...")
        self.count_shoots = 0
        self.shots_left = 9
        self.reloading = False
    
    
    on_target = 0

    dist = 0
    start_check = 0
    #in order to get pos before root initialization on update
    #we created empty Entities to use their attributes
    bullet = Entity()
    target = Entity()

    def fire(self):
        #put target into a condition
        # global target
        
        Audio("audio/fire.mp3")
        
        #self.gun.blink(color.orange)
        #self.gun.color=color.orange
        #print(self.gun)
        """
        blink does not work as intended, and
        messes around with bullet animation
        """
        self.shots_left = 9 - self.count_shoots
        print(f"shots left: {self.shots_left}")
        self.gun.blink(color.orange)
        
        self.bullet = Entity(parent=self.gun, model='cube', collider='box', scale=2, color=color.red)
        self.bullet.world_parent = scene
        ##self.bullet.animate("position", self.bullet.forward*50, duration=0.5, curve=curve.linear)
        self.bullet.animate_position(self.bullet.position+(camera.forward*50), 
            curve=curve.linear, 
            duration=1) #animete pos gun = bullet curve=curve.linear,

        destroy(self.bullet, 2)

    def get_gun(self):
        Audio("audio/click.mp3")
        Audio("audio/reload.mp3")
        self.gun.parent = camera
        self.gun.position = Vec3(.2,-.2,.5)#Vec3(.2,-.5,.5)
        self.gun.rotation_y=90
        #self.player.position = self.gun.position
        #self.player.gun = self.gun

        #self.bullet.position = self.gun.position

        self.player.gun = True
        self.gun_in_hand = True
    
    def input(self, key):
        if key == "g":
            print("getting gun...")
            self.get_gun()
        if key == 'left mouse down' and self.gun_in_hand == True and self.count_shoots <10 and not self.reloading: #self.player.gun
            try:                
                print("calling fire...")
                self.fire()
                self.count_shoots += 1
                print("fire finished")
            except Exception as e:
                #print("something wento wrong")
                print(e)
            finally:
                pass
        elif self.count_shoots == 10:
            print("reloading...")
            self.reloading = True
            wait = timer(.7, self.reload_gun)
            # self.count_shoots == 11
            wait.start()

    def update(self):
        
        try:
            self.dist = distance(self.bullet.world_position, self.target.world_position)
            print("distance: ", self.dist)
        except: 
            print("something went wrong")
        #print(self.dist)
        
        if self.start_check == True:
            #destroy target when dist bullet-target is relatively small
            if self.dist < 1:
                destroy(self.target)
                destroy(self.bullet)

                """
                after the entities are destroyed, we can no longer access its world_pos and other properties
                with that said, after we destroy it we need to set new empty entity holders  with the same varible names
                """
                self.target = Entity()
                self.bullet = Entity()
                self.on_target = 0
                self.start_check = False

        if self.on_target == 0:
            try:
                #to avoid unwanted duplication of target, destroy if any, then recreate
                destroy(self.target)
            except:
                pass
            self.target = Entity(
                model="sphere",
                texture="images/logo.png",
                #collider="sphere",
                color = color.yellow,
                scale=3,
                #collider="box",
                position = (random.randint(-5, 5),random.randint(1, 4), random.randint(-7, 7)),
                double_sided=True,
                visible=True
                )
            self.on_target = 1

            if self.start_check == False:
                self.start_check = True

if __name__ == '__main__':

    root = Ursina()
    root.shader = basic_lighting_shader  # Optional for lighting effects
            
    gun_model = "models/submachine-gun/Tec_9.fbx"
    gun_texture = "models/submachine-gun/Tec_9_low_lambert1_Roughness.jpg"

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

    stand_position  = Entity(
    model="cube",
    texture="grass",
    color=color.orange,
    scale=3,
    collider="box",
    position=(0, -5.5, 5),
    double_sided=True
    )

    

    player = FPC()
    gun = Gun_Controller(gun_model, player, gun_texture)

    root.run()