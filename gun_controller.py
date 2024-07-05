"""
implementation of all gun related stuff,
aiming, shooting, bullet movement, hit detection, raycast etc
"""
from ursina import *
from ursina.shaders import basic_lighting_shader
from ursina.prefabs.first_person_controller import FirstPersonController as FPC
from threading import Timer as timer

class Gun_Controller(Entity):

    def __init__(self, gun_model, player, gun_texture, stand_pos, **kwargs):

        super().__init__()

        self.player = player
        self.player.gun = None
        self.gun_in_hand = False
        self.count_shoots = 0
        self.reloading = False
        self.gun = Button(parent=scene, model=gun_model, 
            #scale=.02/150, #for normal first gun
            scale=.02, #for submachine gun
            texture=gun_texture,
            origin_y=-.5, 
            position=Vec3(0, -2, 5)
            #collider='box', 
            )
        self.gun.on_click = self.get_gun

        self.stand_pos = stand_pos

        self.status_text = Text(
            text="Grab the gun or press \'G\'",
            #font="other/fonts/GILSANUB.TTF",
            y=.35, x=.55,
            scale=.8,
            color=color.green
            )

    def reload_gun(self):
        if self.reloading == True:
            Audio("audio/reload.mp3")
            print("reloaded...")
            self.status_text.text = f"aim & shot \n{self.shots_left}"
        self.count_shoots = 1
        self.shots_left = 9
        self.reloading = False
    
    on_target = 1
    dist = 0
    start_check = False
    #in order to get pos before root initialization on update
    #we created empty Entities to use their attributes
    bullet = Entity()
    target = Entity()


    def fire(self):
        
        Audio("audio/fire.mp3")
        self.shots_left = 9 - self.count_shoots
        print(f"shots left: {self.shots_left}")
        self.gun.blink(color.orange)
        
        self.bullet = Entity(parent=self.gun, model='cube', collider='box', scale=2, color=color.red)
        self.bullet.world_parent = scene
        ##self.bullet.animate("position", self.bullet.forward*50, duration=0.5, curve=curve.linear)
        self.bullet.animate_position(self.bullet.position+(camera.forward*50), 
            curve=curve.linear, 
            duration=.8)
        try:
            destroy(self.bullet, 2.5)
        except:
            print("wrong caught here")

    def get_gun(self):
        Audio("audio/click.mp3")
        Audio("audio/reload.mp3")
        self.gun.parent = camera
        self.gun.position = Vec3(.2,-.2,.5)
        self.gun.rotation_y=90

        self.status_text.text = "stay on the stage"
       
        self.player.gun = True
        self.gun_in_hand = True
        #self.start_check = True
    
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
            except:
                #print("something wento wrong")
                pass
        elif self.count_shoots == 10:
            self.reloading = True
            print("reloading...")
            self.status_text.text = "Reloading..."
            wait = timer(.7, self.reload_gun)
            # self.count_shoots == 11
            wait.start()

    color_list = [color.yellow, color.green, color.blue, color.red, color.orange]
    random_on = True

    #aim wall
    box = Entity()
    show_wall = False

    def change_pos(self, *args):
        self.target2.color = color=random.choice(self.color_list)
        self.target2.position=(random.randint(-10, 10), random.randint(-3, 5), random.randint(19, 35))
        
    def update(self):
        #window.fullscreen = True
        try:
            if self.random_on == True:
                self.random_on = False 
            try:
                """
                assertion problem happens here
                trying to access either bullet/target2 after its been destroyed
                and we did not destoy target2, only changed its color, so
                the main problem is only with the destroyed bullet
                """
                self.dist = distance(self.bullet.world_position, self.target2.world_position) 
                #print("distance: ", self.dist)
            except:
                pass
        except:
            # print("something went wrong")
            pass        

        self.dist2 = distance(self.player.world_position, self.stand_pos.world_position)
        #print("dist2: ",self.dist2)

        if  self.dist2 < 2.1:
            if self.reloading == False:
                try:
                    self.status_text.text = f"aim & shot \n{self.shots_left}"
                except:
                    #skip if no first shooting
                    self.status_text.text = f"aim & shot"
                if self.show_wall == False:
                    self.show_wall = True
                    self.on_target = 0
        else:
            #self.stand_pos.rotation_y += 25 * time.dt
            if self.gun_in_hand == False:
                self.gun.rotation_y += 50 * time.dt
            else:
                self.status_text.text = "stay on the stage"
        
        if self.start_check == True:
            #destroy target when dist bullet-target is relatively small
            if self.dist < 2:
                if self.dist2 < 2.1:
                    

                    self.bullet = Entity()

                    self.random_on = True
                    #self.start_check = False

                    """
                    after the entities are destroyed, we can no longer access its world_pos and other properties
                    with that said, after we destroy it we need to set new empty entity holders  with the same varible names
                    """
                    #self.target = Entity()
                    self.on_target = 0
                

        if self.on_target == 0:
            try:
                #to avoid unwanted duplication of target, destroy if any, then recreate
                destroy(self.target2)
            except:
                pass
            self.target2 = Entity(
                model="cube",
                texture="brick",
                scale=(3,3,3),
                #collider="box",
                double_sided=True,
                )
            self.change_pos()
            self.on_target = 1

            if self.start_check == False:
                self.start_check = True
