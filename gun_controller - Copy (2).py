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
        # self.shots_left = 10 - sewlf.count_shoots
        self.gun = Button(parent=scene, model=gun_model, 
            #color=color.blue,
            #scale=.02/150, #for normal first gun
            scale=.02, #for submachine gun
            texture=gun_texture,
            origin_y=-.5, 
            #position=Vec3(.2,-.5,.5), 
            position=Vec3(0, -2, 5)
            #collider='box', 
            )
        self.gun.on_click = self.get_gun

        self.stand_pos = stand_pos

    def reload_gun(self):
        if self.reloading == True:
            Audio("audio/reload.mp3")
            print("reloaded...")
        self.count_shoots = 0
        self.shots_left = 9
        self.reloading = False
    
    on_target = 0

    dist = 0
    start_check = False
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
            duration=.8) #animete pos gun = bullet curve=curve.linear,

        try:
            destroy(self.bullet, 2.5)
        except:
            print("wrong caught here")
        # self.bullet = Entity()
        #print(len(self.targets_list))

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
        self.start_check = True
    
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

    color_list = [color.yellow, color.green, color.blue, color.red, color.gray, color.white, color.black]
    targets_list = []
    random_on = True

    target2 = Entity()
    
    #aim wall
    box = Entity()
    show_wall = False
    def make_wall(self, *args):
        for i in range(-4, 5):
            for j in range(-10, 10):
                spacing = 1
                scale_box = (3,3,3)
                my_box = Entity(
                model="cube",
                texture="brick",
                color=color.green,
                scale=scale_box,
                #collider="box",
                position=(j*(scale_box[0] + spacing), i*(scale_box[1] + spacing), 30),
                double_sided=True
                )
                self.targets_list.append(my_box)
        print("full list of targets after creation: \n", self.targets_list)
        print("lenght of targets list: ", len(self.targets_list))
    #print("list of targets in the beginning: ", targets_list)
                

    def update(self):

        try:
            if self.random_on == True:
                try:
                    self.target2 = self.targets_list[random.randint(1, len(self.targets_list)-1)]
                    #self.target2 = random.choice(self.targets_list[1:-2])
                    self.target2.color = color.red
                    self.random_on = False 
                    self.start_check = True 
                    print("current target: ", self.target2)
                    print("firsst element: ", self.targets_list[0])
                except:
                    #print(e)
                    pass
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
                print("fault here")
                # pass
        except: 
            # print("something went wrong")
            # print(e)
            pass
        

        self.dist2 = distance(self.player.world_position, self.stand_pos.world_position)
        #print("dist2: ",self.dist2)

        if  self.dist2 < 3.2:
            if self.show_wall == False:
                self.make_wall()
                self.show_wall = True
        else:
            #self.stand_pos.rotation_y += 25 * time.dt
            if self.gun_in_hand == False:
                self.gun.rotation_y += 25 * time.dt
        
        if self.start_check == True:
            #destroy target when dist bullet-target is relatively small
            if self.dist < 1.5:
                # destroy(self.target)
                self.target2.color = color.green
                destroy(self.bullet)

                self.bullet = Entity()

                self.random_on = True
                self.start_check = False

                """
                after the entities are destroyed, we can no longer access its world_pos and other properties
                with that said, after we destroy it we need to set new empty entity holders  with the same varible names
                """
                #self.target = Entity()
                self.bullet = Entity()
                self.on_target = 0
                

        '''if self.on_target == 0:
            try:
                #to avoid unwanted duplication of target, destroy if any, then recreate
                destroy(self.target)
            except:
                pass
            # self.target = Entity(
            #     model="sphere",
            #     texture="images/logo.png",
            #     #collider="sphere",
            #     color = color.yellow,
            #     scale=3,
            #     #collider="box",
            #     position = (random.randint(-5, 5),random.randint(1, 4), random.randint(-7, 7)),
            #     double_sided=True,
            #     visible=True
            #     )
            self.on_target = 1

            if self.start_check == False:
                self.start_check = True'''

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

    stand_pos = Entity(
        model="cube",
        texture="brick",
        color=color.orange,
        scale=3,
        collider="box",
        position=(0, -5, 5),
        double_sided=True
        )

    

    # #aim wall
    # for i in range(-4, 5):
    #     for j in range(-10, 10):
            
    #         spacing = 1
    #         scale_box = (3,3,3)
            
    #         box = Entity(
    #         model="cube",
    #         texture="brick",
    #         color=(random.choice([color.yellow, color.green, color.blue, color.red, color.gray, color.white, color.black])),
    #         scale=scale_box,
    #         #collider="box",
    #         position=(j*(scale_box[0] + spacing), i*(scale_box[1] + spacing), 30),
    #         double_sided=True
    #         )


    # pos2 = stand_position
    # pos2.x =4
    # pos2.color = color.black

    player = FPC()
    gun = Gun_Controller(gun_model, player, gun_texture, stand_pos)

    root.run()