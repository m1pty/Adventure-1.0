# LIBRARIES
import pygame
import random, os

# FILES
import room_rules

# PYGAME PATTERN 
pygame.init()

# параметры окна программы
RES = 900, 630
sc = pygame.display.set_mode(RES)
pygame.display.set_caption('Adventure Atari 2600')

# логотип и fps
icon = pygame.image.load('logo.png')
pygame.display.set_icon(icon)
fps = pygame.time.Clock()

rooms = room_rules.rooms
rules = room_rules.rules
sounds = {'pick_up': 	 pygame.mixer.Sound('assets/sounds/pick-up.mp3'),
		  'put_down': 	 pygame.mixer.Sound('assets/sounds/put-down.mp3'),
		  'moving_down': pygame.mixer.Sound('assets/sounds/moving_down.mp3'),
		  'boom': 		 pygame.mixer.Sound('assets/sounds/boom.mp3'),
		  'final': 		 pygame.mixer.Sound('assets/sounds/final_theme.mp3')}

# открытие ворот
rooms_opened = {'golden': False, 'black': False, 'white': False, 'secret': False}

# НЕТ МАГНИТА И ЛЕТУЧЕЙ МЫШИ

class Item:
	def __init__(self, scene, texture, x, y, room):
		self.scene, self.texture, self.x, self.y, self.room = scene, texture, x, y, room

		# в инвентаре / расстояние по х / расстояние по у
		self.taken = [False, 0, 0]

# мост сквозь стены
class Bridge:
	def __init__(self, scene, texture, x, y, room):
		self.scene, self.texture, self.x, self.y, self.room = scene, texture, x, y, room
		self.taken = [False, 0, 0]
		self.appending = {}
		self.done = False

# монстр-дракон
class Dragon:
	def __init__(self, scene, texture, x, y, room):
		self.scene, self.texture, self.x, self.y, self.room = scene, texture, x, y, room
		self.can_move = True

# игрок
class MainCharacter: 
	def __init__(self, scene, x, y, room):
		self.scene = scene
		self.x = x
		self.y = y
		self.room = room
		self.size = (25, 25)

		# создание предметов
		cup_texture = pygame.image.load('assets/textures/cup.png')
		sword_texture = pygame.image.load('assets/textures/sword.png')
		teleport_texture = pygame.image.load('assets/textures/teleport.png')
		keys_textures = {'golden': pygame.image.load('assets/textures/key_golden.png'),
						 'black': pygame.image.load('assets/textures/key_black.png'),
						 'white': pygame.image.load('assets/textures/key_white.png'),
						 'secret': pygame.image.load('assets/textures/dot.png')}

		self.sword = Item(sc, sword_texture, 150, 490, [4, 4])

		key_golden_place = random.choice([[ 3,  6], [4, 5], [4, 6], [5, 6]]) 
		key_golden_space = random.choice(rules[key_golden_place[1]][key_golden_place[0]]['space'])

		key_white_place = random.choice([[ 3,  6], [4, 5], [4, 6], [5, 6]])
		key_white_space = random.choice(rules[key_white_place[1]][key_white_place[0]]['space'])

		key_black_place = random.choice([[ 3,  6], [4, 5], [4, 6], [5, 6]])
		key_black_space = random.choice(rules[key_black_place[1]][key_black_place[0]]['space'])

		# создание предметов
		self.key_golden = Item(sc, keys_textures['golden'], 
							   random.choice(key_golden_space['x']), 
							   random.choice(key_golden_space['y']), 
							   key_golden_place)

		self.key_black = Item(sc, keys_textures['black'], 
							  random.choice(key_black_space['x']), 
							  random.choice(key_black_space['y']), 
							  key_black_place)

		self.key_white = Item(sc, keys_textures['white'], 
							  random.choice(key_white_space['x']), 
							  random.choice(key_white_space['y']), 
							  key_white_place)

		self.dot = Item(sc, keys_textures['secret'], 68, 520, [3, 6])

		bridge_generation = random.choice([[sc, teleport_texture, 385, 400, [4, 8]], 
										   [sc, teleport_texture,  75, 155, [4, 7]],
										   [sc, teleport_texture,  75, 155, [4, 7]],
										   [sc, teleport_texture,  75, 155, [4, 7]]
										   ])
		
		self.bridge = Bridge(*bridge_generation)

		self.cup = Item(sc, cup_texture, 385, 500, [3, 5])

		self.possible_items = [self.sword, self.key_golden, self.key_black, self.key_white, self.dot, self.bridge, self.cup]

		# создание дракона
		self.dragon_yellow_textures = [pygame.image.load('assets/textures/mobs/dragon_golden.png'), 
								  	   pygame.image.load('assets/textures/mobs/dragon_golden_mouthopen.png'), 
								  	   pygame.image.load('assets/textures/mobs/dragon_golden_dead.png')]
		
		self.dragon_yellow = Dragon(sc, self.dragon_yellow_textures[0], 700, 300, [5, 6]) 

	# отрисовка комнаты, персонажа, мобов и предметов
	def draw_env(self):
		# комната
		self.scene.blit(rooms[self.room[1]][self.room[0]][0], (0, 0))

		# предметы
		for cur_item in self.possible_items:
			if (cur_item.taken[0]):
				self.scene.blit(cur_item.texture, (self.x + cur_item.taken[1], self.y + cur_item.taken[2]))

			else:
				if (cur_item.room == self.room):
					self.scene.blit(cur_item.texture, (cur_item.x, cur_item.y))

		# персонаж
		pygame.draw.rect(self.scene, rooms[self.room[1]][self.room[0]][1], (self.x, self.y, self.size[0], self.size[1]))

		# мобы
		if (self.room == [5, 6]):
			self.scene.blit(self.dragon_yellow.texture, (self.dragon_yellow.x, self.dragon_yellow.y))

	def move(self):
		"""ПЕРЕМЕЩЕНИЕ ПО ПОЛЮ КОМНАТЫ"""

		speed = 2    
		keys = pygame.key.get_pressed()

		# если передвижение на 2 невозможно, двигаемся на 1
		if keys[pygame.K_a]:
			for element in rules[self.room[1]][self.room[0]]['space']:
				if (self.x - 2 in element['x']):
					if (self.y in element['y']) and (self.y + 24 in element['y']):
						self.x -= speed
						break

				elif (self.x - 1 in element['x']):
					if (self.y in element['y']) and (self.y + 24 in element['y']):
						self.x -= (speed - 1)
						break

		if keys[pygame.K_d]:
			for element in rules[self.room[1]][self.room[0]]['space']:
				if (self.x + 26 in element['x']):
					if (self.y in element['y']) and (self.y + 24 in element['y']):
						self.x += speed
						break

				elif (self.x + 25 in element['x']):
					if (self.y in element['y']) and (self.y + 24 in element['y']):
						self.x += (speed - 1)
						break

		if keys[pygame.K_w]:
			for element in rules[self.room[1]][self.room[0]]['space']:
				if (self.y - 2 in element['y']):
					if (self.x in element['x']) and (self.x + 24 in element['x']):
						self.y -= speed
						break

				elif (self.y - 1 in element['y']):
					if (self.x in element['x']) and (self.x + 24 in element['x']):
						self.y -= (speed - 1)
						break

		if keys[pygame.K_s]:
			for element in rules[self.room[1]][self.room[0]]['space']:
				if (self.y + 26 in element['y']):
					if (self.x in element['x']) and (self.x + 24 in element['x']):
						self.y += speed
						break

				elif (self.y + 25 in element['y']):
					if (self.x in element['x']) and (self.x + 24 in element['x']):
						self.y += (speed - 1)
						break


	def check_new_room(self):
		"""ПРОВЕРКА НА ПЕРЕХОД В НОВУЮ КОМНАТУ"""

		# появление на новых координатах в новой комнате, исходя из типа перемещения
		self.teleport = {'up':    {'x': self.x, 'y': 600}, 
						 'down':  {'x': self.x, 'y': 5}, 
						 'left':  {'x': 874,    'y': self.y}, 
						 'right': {'x': 5,      'y': self.y}}

		# если координаты в выходе, то перемещение
		for element in rules[self.room[1]][self.room[0]]['exits']:
			if (self.x in element['x']) and (self.y in element['y']):
				self.room = element['room']
				self.x, self.y = self.teleport[element['mode']]['x'], self.teleport[element['mode']]['y']

	def using_inventory(self):
		"""ПОЗВОЛЯЕТ ПОДНИМАТЬ ИЛИ КЛАСТЬ ПРЕДМЕТЫ"""

		keys = pygame.key.get_pressed()
		if (keys[pygame.K_SPACE]):


			for cur_item in self.possible_items:
				if (cur_item.taken[0]):
					sounds['put_down'].play()
					cur_item.x = self.x + cur_item.taken[1]
					cur_item.y = self.y + cur_item.taken[2]
					cur_item.taken = [False, 0, 0]
					cur_item.room = self.room
					pygame.time.delay(300)

				# если хотим взять
				else:
					if (cur_item.room == self.room):
						if (cur_item != self.bridge):
							if (self.x in range(cur_item.x - 35, cur_item.x + 100)) and (self.y in range(cur_item.y - 35, cur_item.y + 75)):
								sounds['pick_up'].play()
								cur_item.taken = [True, cur_item.x - self.x, cur_item.y - self.y]
								pygame.time.delay(300)
								break # прерывание, чтобы не брались вместе

						else:
							if (self.x in range(cur_item.x - 50, cur_item.x + 185)) and (self.y in range(cur_item.y - 50, cur_item.y + 185)):
								sounds['pick_up'].play()
								cur_item.taken = [True, cur_item.x - self.x, cur_item.y - self.y]
								pygame.time.delay(300)

								for i in range(len(rules[self.room[1]][self.room[0]]['space'])):
									if (rules[self.room[1]][self.room[0]]['space'][i] == self.bridge.appending):
										del rules[self.room[1]][self.room[0]]['space'][i]
										break

								self.bridge.appending = {}
								break # прерывание, чтобы не брались вместе


	def check_doors(self):
		"""ПРОВЕКА НА ОТКРЫТИЕ ДВЕРЕЙ ЗАМКОВ"""

		# GOLDEN GATES
		if (rooms_opened['golden'] == False and self.room == [4, 5]):
			if (self.key_golden.taken[0] and self.x + self.key_golden.taken[1] in range (367, 533) and self.y + self.key_golden.taken[2] in range(425, 498)):
				rooms[5][4] = [pygame.image.load('assets/rooms/04_05_opened.png'), (192, 204,  13)]
				rules[5][4]['space'].append({'x': range(406, 494), 'y': range(  0, 630)})
				rooms_opened['golden'] = True

			elif (not self.key_golden.taken[0] and self.key_golden.room == [4, 5] and self.key_golden.x in range(367, 533) and self.key_golden.y in range(425, 498)):
				rooms[5][4] = [pygame.image.load('assets/rooms/04_05_opened.png'), (192, 204,  13)]
				rules[5][4]['space'].append({'x': range(406, 494), 'y': range(  0, 630)})
				rooms_opened['golden'] = True

		# WHITE GATES
		if (rooms_opened['white'] == False and self.room == [ 4,  9]):
			if (self.key_white.taken[0] and self.x + self.key_white.taken[1] in range (367, 533) and self.y + self.key_white.taken[2] in range(425, 498)):
				rooms[9][4] = [pygame.image.load('assets/rooms/04_09_opened.png'), (223, 222, 228)]
				rules[9][4]['space'].append({'x': range(406, 494), 'y': range(  0, 630)})
				rooms_opened['white'] = True

			elif (not self.key_white.taken[0] and self.key_white.room == [4, 5] and self.key_white.x in range(367, 533) and self.key_white.y in range(425, 498)):
				rooms[9][4] = [pygame.image.load('assets/rooms/04_09_opened.png'), (223, 222, 228)]
				rules[9][4]['space'].append({'x': range(406, 494), 'y': range(  0, 630)})
				rooms_opened['white'] = True

		# BLACK GATES
		if (rooms_opened['black'] == False and self.room == []):
			pass

		# EASTER EGG ROOM 
		if (rooms_opened['secret'] == False and self.room == [5, 6]):
			if (self.dot.taken[0] and self.x + self.dot.taken[1] in range (750, 900) and self.y + self.dot.taken[2] in range( 57, 573)):
				rooms[6][5] = [pygame.image.load('assets/rooms/05_06_opened.png'), (197, 141,  17)]
				rules[6][5]['space'].append({'x': range(750, 900), 'y': range( 57, 572)})
				rooms_opened['secret'] = True

			elif (not self.key_golden.taken[0] and self.dot.room == [5, 6] and self.dot.x in range(750, 900) and self.dot.y in range( 57, 573)):
				rooms[6][5] = [pygame.image.load('assets/rooms/05_06_opened.png'), (197, 141,  17)]
				rules[6][5]['space'].append({'x': range(750, 900), 'y': range( 57, 572)})
				rooms_opened['secret'] = True

	def check_teleport(self):
		"""РЕАЛИЗАЦИЯ ПЕРЕХОДА ЧЕРЕЗ СТЕНЫ"""
		if (self.bridge.taken[0] == False and self.room == self.bridge.room):
			self.bridge.appending = {'x': range(self.bridge.x + 25, self.bridge.x + 100), 'y': range(self.bridge.y - 25, self.bridge.y + 150)}
			if (self.bridge.appending not in rules[self.room[1]][self.room[0]]['space']):
				rules[self.room[1]][self.room[0]]['space'].append(self.bridge.appending)

	def check_win(self):
		"""ПРОВЕРКА ПОБЕДЫ В ГЛАВНОЙ КОМНАТЕ"""
		if (self.cup.taken[0] == True and self.room == [4, 5] and self.x in range(406, 494) and self.y in range(449, 451)):
			sounds['final'].play()
			while True:

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						quit()

					keys = pygame.key.get_pressed()
					if keys[pygame.K_ESCAPE]:
						quit()

				fps.tick(60)

	def move_dragon(self):
		if (self.room == [5, 6] and self.dragon_yellow.can_move == True):
			if (self.x < self.dragon_yellow.x):
				self.dragon_yellow.x -= 1

			if (self.x > self.dragon_yellow.x):
				self.dragon_yellow.x += 1

			if (self.y > self.dragon_yellow.y):
				self.dragon_yellow.y += 1

			if (self.y < self.dragon_yellow.y):
				self.dragon_yellow.y -= 1

			# встреча, смерть
			if (self.x in range(self.dragon_yellow.x - 5, self.dragon_yellow.x - 1) and self.y in range(self.dragon_yellow.y - 10, self.dragon_yellow.y + 50)):
				sounds['boom'].play()
				self.dragon_yellow.texture = self.dragon_yellow_textures[1]

				# ожидание выхода из игры
				while True:
					for event in pygame.event.get():
						if event.type == pygame.QUIT:
							quit()

						keys = pygame.key.get_pressed()
						if keys[pygame.K_ESCAPE]:
							quit()

					fps.tick(60)

			if (self.sword.taken[0] == False and self.sword.room == [5, 6] and self.dragon_yellow.x == self.sword.x + 64 and self.dragon_yellow.y in range(self.sword.y - 90, self.sword.y + 130)):
				self.dragon_yellow.can_move = False
				sounds['moving_down'].play()
				self.dragon_yellow.texture = self.dragon_yellow_textures[2]






# ============== #
#  ГЛАВНЫЙ ЦИКЛ  #
# ============== #
def run_game():
	global sc
	game = True

	# начальный экран с цифрой "3"
	start_screen = pygame.image.load('assets/rooms/start_screen.png')

	timer, timeout = pygame.time.get_ticks, 2000
	stop = timer() + timeout
	
	while True:
		now = timer()
		sc.blit(start_screen, (0, 0))
		if (now > stop):
			break

		fps.tick(60)
		pygame.display.update()

	# создание персонажа
	# cube = MainCharacter(sc, 435, 500, [4, 5])
	cube = MainCharacter(sc, 435, 500, [2, 2])

	while game:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()
		
		cube.draw_env()			# отрисовка окружения
		cube.move()				# попытка движения
		cube.check_new_room()	# проверка на новую комнату
		cube.using_inventory()	# взаимодействие с предметами
		cube.check_teleport()	# проверка на телепорт сквозь стены

		# проверка на открытие дверей
		if (cube.room in ([4, 5], [2, 3], [4, 9], [5, 6])):
			cube.check_doors()

		# проверка на победу (принесённый кубок)
		if (cube.room == [4, 5]):
			cube.check_win()

		# движение драконов
		if (cube.room in [[5, 6], [6, 11]]):
			cube.move_dragon()

		# print(cube.x, cube.y, cube.room)
		
		fps.tick(200)
		pygame.display.update()

run_game()