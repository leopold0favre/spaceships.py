##----------------------------------------------------------------------------##
##INITIALISATION DU CODE##
import pygame
import math
import random
from pygame.locals import *
from math import *
pygame.init()
window=pygame.display.set_mode((640,480))
pygame.display.set_icon(pygame.image.load('icone.png').convert_alpha())
pygame.display.set_caption('spaceships.py')
fps=100
##----------------------------------------------------------------------------##
##MODULE SCORE##
#crée un compteur, dont la valeur (value) peut être modifiée
#à tout moment, et qui peut etre affiché selon des coordonnées fixes (x,y).
#la taille (size), le nombre de chiffres(digits, rajoute des 0 si nécéssaire),
#la couleur (r,g,b) et police (font, importation du fichier) du compteur sont
#requis et pris en compte.
class score():
    def __init__(self,x,y,r,g,b,value,font,size,digits):
        self.x=x
        self.y=y
        self.r=r
        self.g=g
        self.b=b
        self.value=value
        self.font=pygame.font.Font(font,size)
        self.digits=digits
    def disp(self): #affiche le score
        s=list(str(int(self.value)))
        for n in range((self.digits)-(len(s))):
            s.insert(0,"0")
        value="".join(s)
        text=self.font.render(value,1,(self.r,self.g,self.b))
        window.blit(text,(self.x,self.y))
##----------------------------------------------------------------------------##
##MODULE OBJECT##
#crée un objet physique d'une certaine masse (mass), et de coordonnées
#initiales (x,y) dont on pourra appliquer des vitesses, des forces, etc...
#(en 2 dimensions). Son temps d'existence, t, devra être augmenté régulièrement.
class object():
    def __init__(self,mass,x,y):
        self.mass=mass
        self.t=0
        self.x0=x
        self.y0=y
        self.x=x
        self.y=y
        self.vx=0
        self.vy=0
        self.Fx=0
        self.Fy=0
    def strength(self,x,y): #applique un vecteur force F(x,y) sur l'objet
        self.Fx=self.Fx+x
        self.x0=self.x
        self.Fy=self.Fy+y
        self.y0=self.y
        self.t=0
    def speed(self,x,y):    #applique un vecteur vitesse v(x,y) sur l'objet
        self.vx=self.vx+x
        self.x0=self.x
        self.vy=self.vy+y
        self.y0=self.y
        self.t=0
    def reset(self):    #annule les forces et les vitesses aplliquées sur
        self.x0=self.x  #l'objet, le téléporte à sa position initiale
        self.y0=self.y
        self.t=0
        self.vx=0
        self.vy=0
        self.Fx=0
        self.Fy=0
    def update_object(self):    #met l'objet à jour après augmentation du temps t (d'après forces et vitesses)
        self.x=(((self.Fx)/(2*(self.mass)))*(self.t**2))+((self.vx)*self.t)+self.x0
        self.y=(((self.Fy)/(2*(self.mass)))*(self.t**2))+((self.vy)*self.t)+self.y0
    def teleport(self,x,y): #téléporte l'objet aux coordonnées (x,y)
        self.x=x
        self.x0=x
        self.y=y
        self.y0=y
    def slowdown(self,a):   #ralentit la vitesse de l'objet (d'une valeur a) quelle que soit sa trajectoire
        if self.vx!=0 or self.vy!=0:
            self.speed(-(self.vx/sqrt((self.vx**2)+(self.vy**2)))*a,-(self.vy/sqrt((self.vx**2)+(self.vy**2)))*a)
        if sqrt((self.vx**2)+(self.vy**2))<a:
            self.speed(-self.vx,-self.vy)
    def disp_object(self,sprite,window):    #affiche l'objet avec l'image choisie (sprite) sur la fenêtre (window)
        window.blit(sprite,(self.x,self.y,))
    def collision(self,a,x1,y1,x2,y2):  #vérifie si l'objet pénètre (a='out_box') ou sort (a='in_box') d' une certaine
        if a=='in_box':                 #boite de collision. Si oui, il est ramené à sa position précédente.
                if self.x>x2:
                        self.teleport(x2,self.y)
                        self.speed(-self.vx,0)
                if self.x<x1:
                        self.teleport(x1,self.y)
                        self.speed(-self.vx,0)
                if self.y<y1:
                        self.teleport(self.x,y1)
                        self.speed(0,-self.vy)
                if self.y>y2:
                        self.teleport(self.x,y2)
                        self.speed(0,-self.vy)
        if a=='out_box':
              prev_x=self.x
              prev_y=self.y
              self.t=self.t+1/fps
              self.update_object()
              if self.x<x2 and self.x>x1 and self.y>y1 and self.y<y2:
                    if prev_x<=x1:
                        self.teleport(x1,self.y)
                        self.speed(-self.vx,0)
                    if prev_x>=x2:
                        self.teleport(x2,self.y)
                        self.speed(-self.vx,0)
                    if prev_y<=y1:
                        self.teleport(self.x,y1)
                        self.speed(-self.vx,0)
                    if prev_y>=y2:
                        self.teleport(self.x,y2)
                        self.speed(-self.vx,0)
              else:
                    self.teleport(prev_x,prev_y)
                    self.t=self.t-1/fps
##----------------------------------------------------------------------------##
##MODULE SPACESHIP##
#crée un vaisseau qui peut agir comme un objet physique (object), et de
#points de vie (hp), de sprite (sprite) et de sprite de ses projectiles
#(missiles_sprite) sélectionnables.
class spaceship():
    def __init__(self,object,needed_time,hp,missiles_sprite,sprite):
        self.object=object
        self.reload_time=0
        self.needed_time=needed_time
        self.reload=0
        self.hp=hp
        self.maxhp=hp
        self.sprite=sprite
        self.missiles=[]
        self.missiles_sprite=missiles_sprite
    def shoot(self,speed,missile_sfx): #fait tirer un missile au vaisseau
        if self.reload_time==self.needed_time:
            missile=object(1,self.object.x+(pygame.Surface.get_width(self.sprite)/2),self.object.y+(pygame.Surface.get_height(self.sprite)/2))
            missile.speed(speed,0)
            self.missiles.append(missile)
            missile_sfx.play()
            self.reload_time=0
    def auto_reload(self): #augmente la charge des missiles du vaisseau
        if self.reload_time<self.needed_time:
            self.reload_time=self.reload_time+1
    def move(self,speed,max_speed,key,up,left,down,right):  #déplace le vaisseau selon quatre touches et une vitesse au choix
        current_speed=sqrt(((self.object.vx)**2)+((self.object.vy)**2))<max_speed
        if key[up] and current_speed<max_speed:
            self.object.speed(0,-speed)
        if key[down] and current_speed<max_speed:
            self.object.speed(0,speed)
        if key[right] and current_speed<max_speed:
            self.object.speed(speed,0)
        if key[left] and current_speed<max_speed:
            self.object.speed(-speed,0)
    def slowdown(self,speed):   #ralentit le vaisseau
       self.object.slowdown(speed)
    def update(self):   #met à jour la position du vaisseau
        self.object.t=self.object.t+1/fps
        self.object.update_object()
    def display(self,window):   #affiche le vaisseau
        self.object.disp_object(self.sprite,window)
    def update_missiles(self):  #met à jour la position des missiles appartenant au vaisseau
        for i in range(len(self.missiles)):
            self.missiles[i].t=self.missiles[i].t+1/fps
            self.missiles[i].update_object()
            self.missiles[i].disp_object(self.missiles_sprite,window)
    def display_missiles(self,window):  #affiche tout les missiles appartenant au vaisseau
        for i in range(len(self.missiles)):
            self.missiles[i].disp_object(self.missiles_sprite,window)

    def missiles_out_of_range(self,x1,y1,x2,y2):    #désactive les missiles qui sortent d'une certaine zone. Tout missile désactivé devra être supprimé avec delete_missiles
        for i in range(len(self.missiles)):
            if self.missiles[i].x<x1 or self.missiles[i].x>x2 or self.missiles[i].y<y1 or self.missiles[i].y>y2:
                self.missiles[i]=None
    def delete_missiles(self):  #supprime les missiles désactivés d'un vaisseau
        a=0
        for i in range(len(self.missiles)):
            if self.missiles[i]==None:
                a=a+1
        for i in range(a):
            self.missiles.remove(None)
    def missile_hit(self,missiles_list,hp,hit_sfx): #vérifie si un vaisseau est en collision avec un missile d'une liste de missiles. Si oui, sa vie diminue d'une valeur choisie
        for i in range(len(missiles_list)):
            if missiles_list[i]!=None and self!=None:
                if missiles_list[i].x>self.object.x and missiles_list[i].y>self.object.y and missiles_list[i].x<self.object.x+(pygame.Surface.get_width(self.sprite)) and missiles_list[i].y<self.object.y+(pygame.Surface.get_height(self.sprite)):
                    missiles_list[i]=None
                    self.hp=self.hp-hp
                    if self.hp>0:
                        hit_sfx.play()
    def disp_hp_bar(self,sprites,window):   #affiche une petite barre de vie à côté d'un vaisseau
        if self.hp<self.maxhp and self.hp>0:
            i=int(self.hp/(self.maxhp/len(sprites)))-1
            window.blit(sprites[i],(self.object.x+int(pygame.Surface.get_width(self.sprite)/2)-int(pygame.Surface.get_width(sprites[i])/2),self.object.y-2-pygame.Surface.get_height(sprites[i])))
    def disp_big_hp_bar(self,sprite,window,side_of_decay,x,y):  #affiche ma grosse barre de vie d'un vaisseau aux coordonnées choisies, et le côté duquel celle-ci va diminuer
        i=(self.hp/self.maxhp)
        l=pygame.Surface.get_width(sprite)
        if side_of_decay=='left':
            window.blit(pygame.transform.chop(sprite,(0,0,(1-i)*l,0)),(x+(1-i)*l,y))
        elif side_of_decay=='right':
            window.blit(pygame.transform.chop(sprite,(i*l,0,(1-i)*l+10,0)),(x,y))
##----------------------------------------------------------------------------##
##MODULE EXPLOSION##
#crée une explosion animée aux coordonnées choisies
class explosion():
    def __init__(self,x,y,sprites_list):
        self.x=x
        self.y=y
        self.sprites_list=sprites_list
        self.t=0
    def display(self,window): #affiche l'esplosion, avec l'image correspondant à sa durée de vie
        window.blit(self.sprites_list[int(self.t)],(self.x,self.y))
def animate_explosions(explosions_list,frame_step): #met à jour et affiche toutes les explosions d'une liste d'explosions
     for i in range(len(explosions_list)):
        explosions_list[i].t=explosions_list[i].t+1/frame_step
        if explosions_list[i].t>15:
            explosions_list[i]=None
     clear_list(explosions_list)
     for i in range(len(explosions_list)):
        explosions_list[i].display(window)
##----------------------------------------------------------------------------##
##MODULE MENU_BOX##
#crée une case de menu cliquable affichant un texte, aux coordonnées (x,y)
#dont le sprite (sprite_up) se change en sprite_down lorsque la souris survole la case.
#Celle-ci affiche un texte (text) avec une police au choix (font)
class menu_box():
    def __init__(self,sprite_up,sprite_down,x,y,font,text):
        self.sprite_up=sprite_up
        self.sprite_down=sprite_down
        self.x=x
        self.y=y
        self.font=font
        self.text=text
        self.sprite_width=pygame.Surface.get_width(self.sprite_up)
        self.sprite_height=pygame.Surface.get_height(self.sprite_up)
    def check(self,mouse_pos,mouse_left_click,activated): #affiche un sprite en fonction de son statut et retourne une valeur en fonction de celui-ci (libre=0, survolée=1, cliquée=2)
        text_width=pygame.Surface.get_width(font.render(self.text,1,(0,0,0)))
        if mouse_pos[0]>=self.x and mouse_pos[0]<=self.x+self.sprite_width and mouse_pos[1]>=self.y and mouse_pos[1]<=self.y+self.sprite_height:
                window.blit(self.sprite_down,(self.x,self.y))
                window.blit(font.render(self.text,1,(80,80,80)),(self.x+self.sprite_width/2-text_width/2,self.y+8))
                if mouse_left_click and activated:
                    return 2
                else:return 1
        else:
                window.blit(self.sprite_up,(self.x,self.y))
                window.blit(self.font.render(self.text,1,(20,20,20)),(self.x+self.sprite_width/2-text_width/2,self.y+8))
                return 0

##----------------------------------------------------------------------------##
def clear_list(alist):
    a=0
    for i in range(len(alist)):
            if alist[i]==None:
                a=a+1
    for i in range(a):
            alist.remove(None)
##------------------------------------MENUS-----------------------------------##
def menu_aide():
        disp_aide=True
        allow_mlc=False
        returned_choice=0
        while disp_aide:
            mlc=pygame.mouse.get_pressed()[0]
            if mlc==False and allow_mlc==False:allow_mlc=True
            if mlc and allow_mlc:
                returned_choice=None
            window.blit(aide,(150,140))
            if disp_aide:pygame.display.flip()
            pygame.event.pump()
            clock.tick(100)
            for event in pygame.event.get():
                    if event.type==QUIT:
                        returned_choice='quitter'
            if returned_choice==None or returned_choice=='quitter':disp_aide=False
        return returned_choice
def menu_pause():
        pause=True
        allow_escape=False
        allow_mlc=False
        returned_choice=0
        menu_box_1=menu_box(click_textbox,click_textbox_down,276,208,font,'Continuer')
        menu_box_2=menu_box(click_textbox,click_textbox_down,276,246,font,'Contrôles')
        menu_box_3=menu_box(click_textbox,click_textbox_down,276,284,font,'Quitter')
        window.blit(background_shadow,(0,0))
        while pause:
            escape=pygame.key.get_pressed()[K_ESCAPE]
            mouse_pos=pygame.mouse.get_pos()
            mouse_left_click=pygame.mouse.get_pressed()[0]
            window.blit(pause_menu,(150,140))
            result1=menu_box_1.check(mouse_pos,mouse_left_click,allow_mlc and allow_escape)
            result2=menu_box_2.check(mouse_pos,mouse_left_click,allow_mlc and allow_escape)
            result3=menu_box_3.check(mouse_pos,mouse_left_click,allow_mlc and allow_escape)
            if escape==False and allow_escape==False:
                allow_escape=True
            if mouse_left_click==False and allow_mlc==False:
                allow_mlc=True
            if escape and allow_escape:
                allow_escape=False
                returned_choice=None
            if result1==2:returned_choice='continuer'
            if result2==2:
                returned_choice=menu_aide()
                allow_escape=False
                allow_mlc=False
            if result3==2:returned_choice='retour'
            pygame.event.pump()
            clock.tick(100)
            for event in pygame.event.get():
                if event.type==QUIT:
                    returned_choice='quitter'
            if returned_choice=='retour' or returned_choice=='quitter' or returned_choice=='continuer':pause=False
            if pause:pygame.display.flip()
        return returned_choice
##------------------------------MENU PRINCIPAL--------------------------------##
def main_menu():
    main_menu=True
    menu_box_1=menu_box(click_textbox,click_textbox_down,276,247,font,'Duel')
    menu_box_2=menu_box(click_textbox,click_textbox_down,276,297,font,'Survie')
    menu_box_3=menu_box(click_textbox,click_textbox_down,276,345,font,'Contrôles')
    menu_box_4=menu_box(click_textbox,click_textbox_down,535,442,font,'Quitter')
    expl_duel=pygame.font.Font('upheavtt.ttf',14).render("Affrontez un ami sur le même clavier.",1,(255,255,255))
    expl_survie=pygame.font.Font('upheavtt.ttf',14).render("Éliminez un maximum d'ennemis dirigés par l'ordinateur.",1,(255,255,255))
    expl_controles=pygame.font.Font('upheavtt.ttf',14).render("Apprenez comment jouer.",1,(255,255,255))
    expl_quitter=pygame.font.Font('upheavtt.ttf',14).render("Quitter le jeu.",1,(255,255,255))
    allow_mlc=False
    allow_escape=False
    returned_choice=0
    while main_menu:
        escape=pygame.key.get_pressed()[K_ESCAPE]
        mouse_pos=pygame.mouse.get_pos()
        mouse_left_click=pygame.mouse.get_pressed()[0]
        window.blit(menu_principal,(0,0))
        result1=menu_box_1.check(mouse_pos,mouse_left_click,allow_mlc and allow_escape)
        result2=menu_box_2.check(mouse_pos,mouse_left_click,allow_mlc and allow_escape)
        result3=menu_box_3.check(mouse_pos,mouse_left_click,allow_mlc and allow_escape)
        result4=menu_box_4.check(mouse_pos,mouse_left_click,allow_mlc and allow_escape)
        if escape==False and allow_escape==False:
                allow_escape=True
        if mouse_left_click==False and allow_mlc==False:
                allow_mlc=True
        if escape and allow_escape:
                allow_escape=False
                returned_choice='quitter'
        if result1==2:
            returned_choice=duel()
            allow_escape=False
            allow_mlc=False
        elif result1==1:
            window.blit(expl_duel,(5,460))
        if result2==2:
            returned_choice=survie()
            allow_escape=False
            allow_mlc=False
        elif result2==1:
            window.blit(expl_survie,(5,460))
        if result3==2:
            returned_choice=menu_aide()
            allow_escape=False
            allow_mlc=False
        elif result3==1:
            window.blit(expl_controles,(5,460))
        if result4==2:returned_choice='quitter'
        elif result4==1:
            window.blit(expl_quitter,(5,460))
        pygame.event.pump()
        clock.tick(100)
        for event in pygame.event.get():
                if event.type==QUIT:
                    returned_choice='quitter'
        if returned_choice=='quitter':main_menu=False
        if main_menu:pygame.display.flip()
    return returned_choice
##-----------------------------------MODES DE JEU-----------------------------##
##survie
def survie():
    survie=True
    targets=[]
    explosions=[]
    missiles_restants=[]
    compteur=score(590,0,255,255,255,0,'upheavtt.ttf',24,3)
    joueur1=[spaceship(object(10,320,240),40,100,tir_spriteA,spaceship_sprite)]
    dummy=spaceship(object(10,-100,-100),40,100,tir_spriteB,spaceship_sprite)
    font=pygame.font.Font('upheavtt.ttf',40)
    font2=pygame.font.Font('upheavtt.ttf',18)
    defaite_txt=font.render('vous avez été abattu !',1,(255,255,255))
    allow_escape=True
    ia_t=[]
    ia_ts=[]
    ia_t_need=[]
    ia_ts_need=[]
    ia_state=[]
    bgt=0
    t=0
    niveau=1
    returned_value=0
    choix_pause=0
    defaite=False
    while survie:
        key=pygame.key.get_pressed()
        events=pygame.event.get()
        bgt=bgt+2
        #collage des images fixes de fond
        if bgt==640:bgt=0
        window.blit(background,(-bgt,0))
        window.blit(background,(-bgt+640,0))
        window.blit(survie_scoreboard,(0,0))
        animate_explosions(explosions,4)
        #spawn des ennemis
        while len(targets)<int(niveau):
            targets.append(spaceship(object(10,700,random.choice([10,50,90,130,170,210,250,290,330,370,410])),40,100,tir_spriteB,ennemy_spaceship_sprite))
            targets[len(targets)-1].object.speed(-250,0)
            ia_state.append('slowdown')
            ia_t.append(0)
            ia_ts.append(0)
            ia_t_need.append(130)
            ia_ts_need.append(random.randint(100,300))
        #ia des ennemis
        for i in range(len(targets)):
            ia_ts[i]=ia_ts[i]+1
            targets[i].slowdown(2)
            targets[i].object.collision('in_box',30,60,750,410)
            if ia_ts[i]==ia_ts_need[i]:
                targets[i].shoot(-400,missile_sfx)
                ia_ts[i]=0
                ia_ts_need[i]=random.randint(60,100)
            if ia_state[i]=='slowdown':
                ia_t[i]=ia_t[i]+1
                if ia_t[i]==ia_t_need[i]:
                    ia_state[i]=random.choice(['move_up','move_down'])
                    if targets[i].object.y<100:ia_state[i]='move_down'
                    elif targets[i].object.y>370:ia_state[i]='move_up'
                    ia_t[i]=0
                    ia_t_need[i]=random.randint(50,75)
            if ia_state[i]=='move_up' or ia_state[i]=='move_down':
                if ia_state[i]=='move_up':targets[i].object.speed(0,-5)
                elif ia_state[i]=='move_down':targets[i].object.speed(0,5)
                ia_t[i]=ia_t[i]+1
                if ia_t[i]==ia_t_need[i]:
                    ia_state[i]='slowdown'
                    ia_t[i]=0
                    ia_t_need[i]=random.randint(50,75)
        #commandes & actions du joueur
        joueur1[0].move(5,600,key,K_z,K_q,K_s,K_d)
        if key[K_SPACE] and (not defaite):
            joueur1[0].shoot(600,missile_sfx)
        joueur1[0].update_missiles()
        joueur1[0].missiles_out_of_range(-10,-10,640,480)
        joueur1[0].delete_missiles()
        joueur1[0].auto_reload()
        joueur1[0].update()
        joueur1[0].object.collision('in_box',10,60,500,440)
        joueur1[0].slowdown(1)
        joueur1[0].disp_big_hp_bar(big_hp_bar0,window,'left',42,30)
        joueur1[0].missile_hit(missiles_restants,10,hit_sfx)
        #actions du joueur sur les ennemis
        if len(targets)>0:
            for i in range(len(targets)):
                targets[i].missile_hit(joueur1[0].missiles,34,hit_sfx)
                if targets[i].hp<=0:
                    explosions.append(explosion(targets[i].object.x-4,targets[i].object.y-4,explosion_sprites))
                    explosion_sfx.play()
                    compteur.value=compteur.value+1
                    for s in range(len(targets[i].missiles)):
                        dummy.missiles.append(targets[i].missiles[s])
                    niveau=niveau+(1/6)
                    targets[i]=None
                    ia_t[i]=None
                    ia_ts[i]=None
                    ia_t_need[i]=None
                    ia_ts_need[i]=None
                    ia_state[i]=None
        clear_list(targets)
        clear_list(ia_t)
        clear_list(ia_ts)
        clear_list(ia_t_need)
        clear_list(ia_ts_need)
        clear_list(ia_state)
        #mises à jour joueur
        joueur1[0].delete_missiles()
        joueur1[0].display_missiles(window)
        if (not defaite):joueur1[0].display(window)

        #commandes & actions des ennemis
        for i in range(len(targets)):
            targets[i].update()
            targets[i].display(window)
            targets[i].update_missiles()
            targets[i].missiles_out_of_range(-10,-10,640,480)
            targets[i].delete_missiles()
            targets[i].auto_reload()
            if targets[i].hp<targets[i].maxhp:
                targets[i].disp_hp_bar(hpbar_sprites,window)
            joueur1[0].missile_hit(targets[i].missiles,5,hit_sfx)
            targets[i].delete_missiles()
            targets[i].display_missiles(window)
            targets[i].display(window)

        #réglage des missiles sans propriétaire
        dummy.update_missiles()
        dummy.missiles_out_of_range(-10,-10,640,480)
        joueur1[0].missile_hit(dummy.missiles,5,hit_sfx)
        dummy.delete_missiles()
        dummy.display_missiles(window)

        #affichage du compteur
        compteur.disp()

        ##PAUSE##
        if key[K_ESCAPE]==False and allow_escape==False:
                allow_escape=True
        if key[K_ESCAPE] and allow_escape:
            choix_pause=menu_pause()
            if choix_pause=='quitter':returned_value='quitter'
            if choix_pause=='continuer':allow_escape=False
            if choix_pause=='retour':returned_value='retour'
        #########

        #activation de défaite
        if joueur1[0].hp<=0 and (not defaite):
            defaite=True
            explosions.append(explosion(joueur1[0].object.x,joueur1[0].object.y,explosion_sprites))
            explosion_sfx.play()
            allow_mlc=False

        #actions post-défaite
        if defaite:
            window.blit(defaite_txt,(100,135))
            window.blit(font2.render(('vous avez détruit %d vaisseaux ennemis.'%compteur.value),1,(255,255,255)),(100,164))
            window.blit(clicktoquit,(10,470-pygame.Surface.get_height(clicktoquit)))
            mouse_left_click=pygame.mouse.get_pressed()[0]
            if mouse_left_click==False and allow_mlc==False:
                allow_mlc=True
            if mouse_left_click and allow_mlc:
                returned_value='retour'

        #actions de fin de frame
        clock.tick(100)
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type==QUIT:
                returned_value='quitter'
        if returned_value=='quitter' or returned_value=='retour':
            survie=False
        if survie:pygame.display.flip()
    return returned_value
##duel
def duel():
    duel=True
    victory=[False,'']
    allow_mlc=False
    explosions=[]
    victoire_j1=pygame.font.Font('upheavtt.ttf',40).render('victoire du joueur 1 !',1,(0,93,3))
    victoire_j2=pygame.font.Font('upheavtt.ttf',40).render('victoire du joueur 2 !',1,(93,15,0))
    score1=score(5,0,255,255,255,0,'upheavtt.ttf',24,3)
    score2=score(610,0,255,255,255,0,'upheavtt.ttf',24,3)
    joueurs=[spaceship(object(10,50,240),40,100,tir_spriteA,spaceship_sprite),spaceship(object(10,590,240),40,100,tir_spriteB,ennemy_spaceship_sprite)]
    allow_escape=True
    allow_mlc=True
    bgt=0
    t=0
    returned_value=0
    choix_pause=0
    while duel:
        key=pygame.key.get_pressed()
        events=pygame.event.get()

        #collage des images fixes & du fond
        bgt=bgt+2
        if bgt==640:bgt=0
        window.blit(background,(-bgt,0))
        window.blit(background,(-bgt+640,0))
        window.blit(duel_scoreboard,(0,0))
        animate_explosions(explosions,10)
        #commandes & actions du joueur 1
        if victory[1]!=1:
            joueurs[0].move(5,600,key,K_z,K_q,K_s,K_d)
            if key[K_SPACE]:
                joueurs[0].shoot(600,missile_sfx)
            joueurs[0].update_missiles()
            joueurs[0].missiles_out_of_range(-10,-10,640,480)
            if not victory[0]:joueurs[0].missile_hit(joueurs[1].missiles,10,hit_sfx)
            else:
                joueurs[1].update_missiles()
                joueurs[1].missiles_out_of_range(-10,-10,640,480)
                joueurs[1].delete_missiles()
            joueurs[0].delete_missiles()
            joueurs[1].delete_missiles()
            joueurs[0].auto_reload()
            joueurs[0].update()
            joueurs[0].slowdown(1)
            joueurs[0].object.collision('in_box',10,60,290,440)
            joueurs[0].display_missiles(window)
            joueurs[0].display(window)
            joueurs[0].disp_big_hp_bar(big_hp_bar0,window,'left',42,30)

        #commandes & actions du joueur 2
        if victory[1]!=0:
            joueurs[1].move(5,600,key,K_UP,K_LEFT,K_DOWN,K_RIGHT)
            if key[K_KP0]:
                joueurs[1].shoot(-600,missile_sfx)
            joueurs[1].update_missiles()
            joueurs[1].missiles_out_of_range(-10,-10,640,480)
            if not victory[0]:joueurs[1].missile_hit(joueurs[0].missiles,10,hit_sfx)
            else:
                joueurs[0].update_missiles()
                joueurs[0].missiles_out_of_range(-10,-10,640,480)
                joueurs[0].delete_missiles()
            joueurs[1].delete_missiles()
            joueurs[0].delete_missiles()
            joueurs[1].auto_reload()
            joueurs[1].update()
            joueurs[1].slowdown(1)
            joueurs[1].object.collision('in_box',320,60,600,440)
            joueurs[1].display_missiles(window)
            joueurs[1].display(window)
            joueurs[1].disp_big_hp_bar(big_hp_bar1,window,'right',374,30)

        #actions post-victoire
        if victory[0]:
            window.blit(clicktoquit,(10,470-pygame.Surface.get_height(clicktoquit)))
            if victory[1]==0:window.blit(victoire_j1,(100,135))
            if victory[1]==1:window.blit(victoire_j2,(100,135))
            mouse_left_click=pygame.mouse.get_pressed()[0]
            if mouse_left_click==False and allow_mlc==False:
                allow_mlc=True
            if mouse_left_click and allow_mlc:
                returned_value='retour'

        #activation de la victoire
        if joueurs[1].hp<=0 and (not victory[0]):
            victory[0]=True
            victory[1]=0
            explosions.append(explosion(joueurs[1].object.x,joueurs[1].object.y,explosion_sprites))
            explosion_sfx.play()
            allow_mlc=False
        if joueurs[0].hp<=0 and (not victory[0]):
            victory[0]=True
            victory[1]=1
            explosions.append(explosion(joueurs[0].object.x,joueurs[0].object.y,explosion_sprites))
            explosion_sfx.play()
            allow_mlc=False

        ##PAUSE##
        if key[K_ESCAPE]==False and allow_escape==False:
                allow_escape=True
        if key[K_ESCAPE] and allow_escape:
            choix_pause=menu_pause()
            if choix_pause=='quitter':returned_value='quitter'
            if choix_pause=='continuer':
                allow_escape=False
                allow_mlc=False
            if choix_pause=='retour':returned_value='retour'
        #########

        #actions de fin de frame
        clock.tick(100)
        pygame.display.flip()
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type==QUIT:
                returned_value='quitter'
        if returned_value=='quitter' or returned_value=='retour':
            duel=False
        if duel:pygame.display.flip()
    return returned_value
##----------------------------------------------------------------------------##
##CONSTANTES##
##sprites
spaceship_sprite=pygame.image.load('images/vaisseaux/vaisseau1.png').convert_alpha()
ennemy_spaceship_sprite=pygame.image.load('images/vaisseaux/vaisseau2.png').convert_alpha()
tir_spriteA=pygame.image.load('images/vaisseaux/missileA.png').convert_alpha()
tir_spriteB=pygame.image.load('images/vaisseaux/missileB.png').convert_alpha()
background=pygame.image.load('images/vaisseaux/background.png').convert_alpha()
background_shadow=pygame.image.load('images/menus/background_shadow.png').convert_alpha()
pause_menu=pygame.image.load('images/menus/pause_menu.png').convert_alpha()
menu_principal=pygame.image.load('images/menus/ecran_titre.png').convert_alpha()
aide=pygame.image.load('images/menus/aide.png').convert_alpha()
click_textbox=pygame.image.load('images/menus/click_textbox.png').convert_alpha()
click_textbox_down=pygame.image.load('images/menus/click_textbox_down.png').convert_alpha()
duel_scoreboard=pygame.image.load('images/menus/duel_scoreboard.png').convert_alpha()
survie_scoreboard=pygame.image.load('images/menus/survie_scoreboard.png').convert_alpha()
clicktoquit=pygame.image.load('images/menus/clictoquit.png').convert_alpha()
##sprites animés
explosion_sprites=[]
for i in range(1,17):explosion_sprites.append(pygame.image.load('images/explosions/exp%d.png' % i).convert_alpha())
hpbar_sprites=[]
for i in range(1,15):hpbar_sprites.append(pygame.image.load('images/barres de vie/hpbar%d.png' % i).convert_alpha())
for i in range(len(explosion_sprites)):
    explosion_sprites[i]=pygame.transform.scale(explosion_sprites[i],(pygame.Surface.get_width(ennemy_spaceship_sprite)+8,pygame.Surface.get_height(ennemy_spaceship_sprite)+8))
big_hp_bar1=pygame.image.load('images/barres de vie/big_hp_bar.png').convert_alpha()
big_hp_bar0=pygame.transform.flip(pygame.image.load('images/barres de vie/big_hp_bar.png').convert_alpha(),False,True)
##effets sonores
menu_musique=pygame.mixer.music.load('sons/theme1.wav')
clock=pygame.time.Clock()
missile_sfx=pygame.mixer.Sound('sons/shot.wav')
explosion_sfx=pygame.mixer.Sound('sons/explosion.wav')
hit_sfx=pygame.mixer.Sound('sons/hit_missile.wav')
##police de caractère
font=pygame.font.Font('upheavtt.ttf',13)
##constantes booléennes & programme
allow_escape=True
t=0
pygame.mixer.music.play(-1,0)
a=main_menu()
if a=='quitter' or a=='retour':
 pygame.quit()