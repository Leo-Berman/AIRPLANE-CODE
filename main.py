#!/usr/bin/env python3
import blessed
import time
import keyboard
import random
''' HELPFUL ABBREVIATIONS
TMC = THE_MAIN_CHARACTER
'''

term = blessed.Terminal()
platform_height = term.height - term.height//4
class GameObject:
	x = 0
	y = 0
	x_previous = 0
	y_previous = 0
	character = ""

	def __init__(self, in_x, in_y, in_character):
		self.x = in_x
		self.y = in_y
		self.character = in_character

	def move_character(self, x_move=0, y_move=0):
		self.x_previous = self.x
		self.y_previous = self.y
		self.x += x_move
		self.y += y_move

class Meteor(GameObject):
	# Added buffer because not necessarily all of the eater will be usable space
	def __init__(self, terminal_width, buffer):
		super().__init__(random.randint(buffer, terminal_width-buffer-1), 0, '*')
	def progress(self):
		self.move_character(0, 1)
		pass

class Eater(GameObject):
	def __init__(self, in_x, in_y, eater_size):
		super().__init__(in_x, in_y, '(*|' + ('_' * (eater_size)) + '|*)')

# must be a GameObject
def move_object(character):
	print(term.move_yx(character.y_previous, character.x_previous),' ' * len(character.character))
	print(term.move_yx(character.y, character.x), character.character)

def remove_object(character):
	print(term.move_yx(character.y, character.x), ' ' * len(character.character))

def remove_object_pre_move(character):
	print(term.move_yx(character.y_previous, character.x_previous), ' ' * len(character.character))

def main():
	TMC = Eater(0, platform_height - 1, term.width//10);
	meteors = []
	broken_platforms = set()
	score = 0
	start_meteor_spawn_time = 3
	start_meteor_render_time = .1
	start_key_streak_multiplier = 10
	start_score_increase = 1
	meteor_spawn_time = start_meteor_spawn_time
	meteor_render_time = start_meteor_render_time
	key_streak_multiplier = start_key_streak_multiplier
	score_increase = start_score_increase
	with term.fullscreen(), term.cbreak(), term.hidden_cursor():
		print(term.clear + term.normal)
		print(term.move_yx(platform_height, 0) + "=" * term.width)
		print(term.move_yx(TMC.y, TMC.x), TMC.character)
		start_width = term.width
		last_meteor_spawn_time = time.time()
		last_meteor_render_time = time.time()
		safe_zone = (TMC.x + 2, TMC.x + len(TMC.character) - 2)
		left_key_streak = 0
		right_key_streak = 0
		while True:
			key = term.inkey(timeout=0.05)
			if key:
				if key.name == 'KEY_LEFT':
					distance_to_move = -1 -(left_key_streak // key_streak_multiplier)
					if not (TMC.x + distance_to_move <= 0):
						TMC.move_character(x_move = distance_to_move)
						left_key_streak += 1
						right_key_streak = 0
					else:
						TMC.move_character(x_move = -1 * TMC.x)
				elif key.name == 'KEY_RIGHT':
					distance_to_move = 1 + (right_key_streak // key_streak_multiplier)
					if not(TMC.x + distance_to_move + len(TMC.character) -1 >= start_width - 1):
						TMC.move_character(x_move = distance_to_move)
						right_key_streak += 1
						left_key_strea = 0
					else:
						TMC.move_character(x_move = start_width - len(TMC.character) - TMC.x - 1)
				else:
					continue
				move_object(TMC)
				safe_zone = (TMC.x + 2, TMC.x + len(TMC.character) - 3)
			else:
				left_key_streak = 0
				right_key_streak = 0
			if time.time() - last_meteor_spawn_time >= meteor_spawn_time:
				last_meteor_spawn_time = time.time()
				# 3 is the (*| part of TMC
				meteors.append(Meteor(start_width, 3))
			if time.time() - last_meteor_render_time >= meteor_render_time:
				last_meteor_render_time = time.time()
				to_delete_meteors = []
				for i,meteor in enumerate(meteors):
					meteor.progress()
					if meteor.y == platform_height - 1:
						if (meteor.x <= safe_zone[0] and meteor.x >= safe_zone[0] - 2):
							return score
						if (meteor.x >= safe_zone[1] and meteor.x <= safe_zone[1] + 2):
							return score
						if not (meteor.x > safe_zone[0] and meteor.x < safe_zone[1]):
							remove_object_pre_move(meteor)
							to_delete_meteors.append(i)
							if meteor.x in broken_platforms:
								return score
							broken_platforms.add(meteor.x)
						else:
							move_object(meteor)
					elif meteor.y >= platform_height:
						move_object(meteor)
						to_delete_meteors.append(i)
						print(term.move_yx(platform_height, meteor.x), ' ')
						score += score_increase
					else:
						move_object(meteor)
				for i, meteor_index in enumerate(to_delete_meteors):
					meteors.pop(meteor_index - i)
				platform_to_print = ("=" * term.width)
				for i in broken_platforms:
					platform_to_print = platform_to_print[0:i+1] + "x" + platform_to_print[i+2:start_width]
				print(term.move_yx(platform_height, 0) + platform_to_print)
				print(term.move_yx(0,0) + str(score))
				if score // 10 >= score_increase:
					meteor_spawn_time -= start_meteor_spawn_time * (.01 * (score//10))
					meteor_render_time -= start_meteor_render_time * (.01 * (score//10))
					score_increase = score // 10 + 1
					if key_streak_multiplier > 1:
						key_streak_multiplier = start_key_streak_multiplier - score // 100
						if key_streak_multiplier < 0:
							key_streak_multiplier = 1
if __name__ == "__main__":
	score = main()
	print("You Scored",score)
