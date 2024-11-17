import pygame, core_functs
class Animation:
    def __init__(self, file_path, duration=5, offset = [0, 0], colorkey=(255, 255, 255)):
        self.frames = self.animation_cutter(pygame.image.load(file_path).convert(), colorkey=colorkey)
        self.index = 0
        self.index_step = 1
        self.index_scope = (0, len(self.frames) - 1)
        self.offset = offset
        self.duration = duration 
        self.game_frames = 0
        self.special_frames = []
        #loop variable decides whether to reset the index once it reaches the max index
        self.loop = True
        #timer_switch updates to True through AnimationManager class every time it sets the timer for the animation
        #niche variable
        self.timer_switch = False
        self.auto = True
        self.end = False
        
    #returns a sequence of frames in the form of a list
    def animation_cutter(self, img, colorkey=(255, 255, 255)):
        width = 0
        lst = []
        for x in range(img.get_width()):
            if img.get_at((x, 0))[0] == 127:
                frame = core_functs.cut(img, x - width, 0, width, img.get_height())
                frame.set_colorkey(colorkey)
                lst.append(frame)
                width = 0
            else: width += 1
        
        return lst

    def reset_scope(self):
        self.index_scope = (0, len(self.frames) - 1)

    #"oh a setter function isn't necessary in py--" stfu. It's good practice.
    def set_mode(self, boolean):
        self.auto = boolean

    def set_loop(self, boolean):
        self.loop = boolean

    def set_index(self, index):
        self.index = index

    def set_index_step(self, step):
        self.index_step = step

    def get_surf(self ,index=None, flip = False):
        if index == None:
            return pygame.transform.flip(self.frames[self.index].copy(), flip, False)
        else: return pygame.transform.flip(self.frames[index].copy(), flip, False)
    
    def get_mask(self, index=None, flip=False):
        if index == None:
            return pygame.mask.from_surface(self.get_surf(flip = flip))
        else: return pygame.mask.from_surface(self.get_surf(index, flip = flip))

    def set_offset(self, lst):
        self.offset = lst

    def get_offset(self, surf, rect, flip):
        offset = self.offset.copy()
        if flip: offset[0] = -offset[0]
        #offset away from real coords since animations are horizontally centered through a rect
        horizontal_offset = (rect.width/2) - (surf.get_width()/2)

        return (horizontal_offset + offset[0], offset[1] + rect.height - surf.get_height()) 

    def update_animation_index(self,  dt):
        self.game_frames = (core_functs.clamp(self.game_frames + dt, (0, self.duration))) % self.duration

        if self.game_frames == 0:
            if self.index == self.index_scope[1]:
                if self.loop:
                    self.index = self.index_scope[0]

            #could've done self.index += 1 but I feel paranoid about it so Imma use clamp
            self.index = round(core_functs.clamp(self.index +  self.index_step * dt, self.index_scope))

    def play(self, surf, rect, flip, scroll = [0, 0], fill=False, dt=1, frame_scale=[1, 1]):
        if self.auto:
            self.update_animation_index(dt)
        
        anim_img = self.frames[self.index].copy()

        frame_scale = [round(frame_scale[i], 2) for i in range(2)]
        
        if frame_scale != [1, 1]:
            anim_img = pygame.transform.scale(anim_img, [anim_img.get_size()[i] * frame_scale[i] for i in range(2)])

        animation_offset = self.get_offset(anim_img, rect, flip)

        if fill:
            fill_surf = pygame.mask.from_surface(self.get_surf(flip=flip)).to_surface(unsetcolor=(0, 0, 0, 0))

            surf.blit(fill_surf, (rect.x + animation_offset[0] - scroll[0], rect.y + animation_offset[1] - scroll[1]))
        
        else:
            surf.blit(pygame.transform.flip(anim_img, flip, False), (rect.x + animation_offset[0] - scroll[0], rect.y + animation_offset[1] - scroll[1]))

        return animation_offset

    def get_current_frame(self):
        return self.frames[self.index].copy()
    
    #returns frame progress from 0 - 1
    def get_frame_progress(self):
        return self.index / (len(self.frames) - 1)

    def set_special_frames(self, lst):
        self.special_frames = lst
        
    def check_special_frames(self):
        if self.index in self.special_frames: 
            return True

    def get_full_duration(self):
        return len(self.frames) * self.duration

class AnimationManager:
    def __init__(self, file_path, duration=5, animation_types=[]):
        self.duration = duration
        self.file_path = file_path

        self.animations = {}
        
        if len(animation_types):
            self.add_animation(*animation_types)

        #used for animations with lock states
        self.animation_timer = AnimationTimer()

        for i in self.animations.keys():
            setattr(self, i, self.animations[i])

    def __getitem__(self, item):
        return getattr(self, item)

    def add_animation(self, *animation_type):
        for i in animation_type:
            if i not in self.animations.keys():
                self.animations[i] = self.animate_path(self.file_path, i, self.duration)
                setattr(self, i, self.animations[i])

        self.action = list(self.animations.keys())[0]

    def animate_path(self, path, animation_type, duration):
        return Animation(path + '/' + animation_type + '.png', duration, [0, 0])

    def get_index(self):
        return self[self.action].index

    def reset_timer(self):
        self.animation_timer.reset_timer()

    def update_timer(self, dt=1):
        self.animation_timer.update_timer(dt=dt)
    
    def set_timer(self, animation_type):
        self.animation_timer.set_timer(animation_type, self[animation_type].get_full_duration())  
        self[animation_type].timer_switch = True

    def check_timer(self, *animation_type):
        return self.animation_timer.check_timer(*animation_type)
    
    def get_timer(self):
        return round(self.animation_timer.timer)

    def get_timer_animation(self):
        return self.animation_timer.animation_type

    #returns [timer, animation_type]
    def get_timer_info(self):
        return [self.get_timer(), self.get_timer_animation()]

    def activate_timer(self, boolean):
        self.animation_timer.active = boolean

    def play(self, surf, action, rect, flip, scroll, fill=False, dt=1, frame_scale=[1, 1]):
        if self.action != action:
            self[self.action].set_index(0)
            self[self.action].reset_scope()
            self.action = action

        return self[self.action].play(surf, rect, flip, scroll, fill, dt=dt, frame_scale=frame_scale)

    def animation_end(self, *animation_types):
        for animation_type in animation_types:
            if self[animation_type].get_frame_progress() == 1 or not self.check_timer(animation_type):
                if self[animation_type].timer_switch:
                    self[animation_type].timer_switch = False
                    return True

class AnimationTimer:
    def __init__(self):
        self.animation_type = None
        self.timer = 0
        self.active = True
        
    def set_timer(self, animation_type, duration):
        self.animation_type = animation_type
        self.timer = duration
    
    def reset_timer(self):
        self.__init__()

    def update_timer(self, dt=1):
        if self.active:
            if self.timer > 0:
                self.timer = core_functs.clamp(self.timer - dt, [0, 1000])

    def check_timer(self, *animation_type):
        if self.timer > 0:
            for i in animation_type:
                if self.animation_type == i:
                    return True
    
