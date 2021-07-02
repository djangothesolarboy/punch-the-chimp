import os, sys
import pygame
from pygame.locals import *

# warning message if font or mixer module aren't available
if not pygame.font:
	print('Warning, fonts disabled.')
if not pygame.mixer:
	print('Warning, mixers disabled.')

# 							RESOURCE LOADING						#
def load_image(name, colorkey=None): # colorkey is used in graphics to represent a color of the image that is transparent
	fullname = os.path.join('data', name)
	try:
		image = pygame.image.load(fullname)
	except pygame.error as message:
		print('Cannot load image:', name)
		raise SystemExit(message)
	image = image.convert()
	if colorkey is not None:
		if colorkey == -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	return image, image.get_rect()

def load_sound(name):
	class NoneSound:
		def play(self): pass
	if not pygame.mixer:
		return NoneSound()
	fullname = os.path.join('data', name)
	try:
		sound = pygame.mixer.Sound(fullname)
	except pygame.error as message:
		print('Cannot load sound:', fullname)
		raise SystemExit(message)
	return sound

# 							GAME OBJECT CLASSES						#
class Fist(pygame.sprite.Sprite):
	"""moves a clenched fist on the screen, following the mouse."""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) # call Sprite initializer
		self.image, self.rect = load_image('fist.bmp', -1)
		self.punching = 0

	def update(self):
		"""move the fist based on the mouse position"""
		pos = pygame.mouse.get_pos()
		self.rect.midtop = pos
		if self.punching:
			self.rect.move_ip(5, 10)

	def punch(self, target):
		"""returns true if the fist collides with the target"""
		if not self.punching:
			self.punching = 1
			hitbox = self.rect.inflate(-5, -5)
			return hitbox.colliderect(target.rect)

	def unpunch(self):
		"""called to pull the fist back"""
		self.punching = 0

class Chimp(pygame.sprite.Sprite):
	"""moves a monkey across the screen. it can spin the monkey when punched"""
	def __init__(self):
		pygame.sprite.Sprite.__init__(self) # call Sprite initializer
		self.image, self.rect = load_image('chimp.bmp', -1)
		screen = pygame.display.get_surface()
		self.area = screen.get_rect()
		self.rect.topleft = 10, 10
		self.move = 9
		self.dizzy = 0
		self.score=0

	def update(self):
		"""walk or spin, depending on the monkeys state"""
		if self.dizzy:
			self._spin()
		else:
			self._walk()

	def _walk(self):
		"""moves the monkey across the screen, and turn at the ends"""
		newpos = self.rect.move((self.move, 0))
		if not self.area.contains(newpos):
			if self.rect.left < self.area.left or self.rect.right > self.area.right:
				self.move = -self.move
				newpos = self.rect.move((self.move, 0))
				self.image = pygame.transform.flip(self.image, 1, 0)
			self.rect = newpos

	def _spin(self):
		"""spin the monkey image"""
		center = self.rect.center
		self.dizzy += 12
		if self.dizzy >= 360:
			self.dizzy = 0
			self.image = self.original
		else:
			rotate = pygame.transform.rotate
			self.image = rotate(self.original, self.dizzy)
		self.rect = self.image.get_rect(center=center)

	def punched(self):
		"""this will cause the monkey to start spinning"""
		if not self.dizzy:
			self.dizzy = 1
			self.original = self.image

def main():
	"""this function is called when the program starts.
	initializes everything it needs, 
	then runs in a loop until the function returns"""

	# initialize everything
	pygame.init()
	screen = pygame.display.set_mode((468, 60))
	pygame.display.set_caption('monkey punching fun')
	pygame.mouse.set_visible(0)

	# create background
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((250, 250, 250))

	score=0

	# text on background, centered
	if pygame.font:
		font = pygame.font.SysFont('monospace', 36)
		text = font.render('Pummel the chimp!', 1, (10, 10, 10))
		textpos = text.get_rect(centerx=background.get_width()/2)
		background.blit(text, textpos)

	# display background
	screen.blit(background, (0, 0))
	pygame.display.flip()

	# prepare game objects
	whiff_sound = load_sound('whiff.wav')
	punch_sound = load_sound('punch.wav')
	chimp = Chimp()
	fist = Fist()
	allsprites = pygame.sprite.RenderPlain((fist, chimp))
	clock = pygame.time.Clock()

	# main loop
	while 1:
		clock.tick(60)

		# handle input events
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				return
			elif event.type == MOUSEBUTTONDOWN:
				if fist.punch(chimp):
					score+=1
					punch_sound.play() # punch
					chimp.punched()
				else:
					whiff_sound.play() # miss
			elif event.type == MOUSEBUTTONUP:
				fist.unpunch()

		# update sprites
		allsprites.update()

		# draw everything
		screen.blit(background, (0, 0))
		allsprites.draw(screen)
		text=font.render('Score: {0}'.format(score),1,(15,15,15))
		screen.blit(text,(0,25))
		pygame.display.flip()

main()