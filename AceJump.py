import sublime, sublime_plugin
from re import search, match, escape


hints_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
hints_letters_length = len(hints_letters)

selection_regex = r'(?=\S){}\S*'
# selection_regex = r'\b%s\S*'

words = [] # That's bad


def number_to_letters(number):
	# Like in excel columns
	base = hints_letters_length
	string = ""
	while number:
		m = (number - 1) % base
		string += hints_letters[m]
		number = (number - m) // base
	return string[::-1]

def letters_to_number(string):
	string = string[::-1]
	base = hints_letters_length
	quantity = len(string)
	number = 0
	for i in range(quantity):
		number += (int(string[i], 36) - 9) * pow(base, i)
	return number


'''
What are we gonna do here? (function activated)
	get first character
	search all words in the current view starting with this letter and label them
	jump to selected word (and select if modifier activated)
'''

class AceJumpCommand(sublime_plugin.WindowCommand):

	def run(self):
		# TODO Add settings
		self.view = self.window.active_view()
		# Will contain all words pasujace to selection_regex % self.char
		#self.words = []
		# Character we are looking for
		self.char = ""
		# Target label (and modifer)
		self.target = ""
		# Tells if labels are shown
		self.labels = False
		self.view.set_status("AceJump", "Seach for character")

		self.window.show_input_panel(
			"AceJump prompt", "",
			self.input, self.change, self.nope
		)

	def input(self, command):
		# Got user input, disable labels and jump
		self.nope()
		self.jump()

	def change(self, command):
		if not command:
			# If user entered text, deleted it and started over
			if self.labels:
				#self.unlabel_words()
				self.view.run_command("search_and_label", {"char": ""})
			self.view.set_status("AceJump", "Type target character")
			return
		if len(command) == 1:
			# Just first character
			self.char = command
			if not self.labels:
				self.view.run_command("search_and_label", {"char": self.char})
				self.labels = True
				#self.search_and_label_words()
		if len(command) > 1:
			# Label (and modifers)
			self.target = command[1:]
			self.view.set_status("AceJump", "Target: {}".format(self.target))

	def nope(self):
		# User cancelled input
		if self.labels:
			#self.unlabel_words()
			self.view.run_command("search_and_label", {"char": ""})
		self.view.erase_status("AceJump")
		# if caller != input:
		sublime.status_message("AceJump: Cancelled")

	def jump(self):
		# TODO Last jump position, so you can jump back with one letter shortcut
		# TODO Settings: add default jump mode
		# TODO Add select_to modifier
		# Get label and modifier
		result = search(r'(\w+)(.?)', self.target)
		if result:
			label = result.group(1).lower()
			modifier = result.group(2)
		else:
			sublime.status_message("Bad input!")
			return
		# Convert label to number, and get its region
		index = letters_to_number(label) - 1
		#if not words:
		#	self.view.run_command("search_and_label", {"char": ""})
		#	return
		region = words[index]
		self.view.run_command("search_and_label", {"char": ""})
		# Do modified (or not modified) jump!
		if modifier == '$' or modifier == '.':
			# End of word
			self.view.run_command("jump_to_place", {"start": region.end()})
			return
		if modifier == '+' or modifier == ',':
			# Select word
			self.view.run_command("jump_to_region", {"start": region.begin(), "end": region.end()})
			return
		sublime.status_message(
			"Search key: {}, go to: {}{}".format(self.char, label, "" if not modifier else ", no such modifier, just jumping")
		)
		self.view.run_command("jump_to_place", {"start": region.begin()})


class SearchAndLabelCommand(sublime_plugin.TextCommand):

	def run(self, edit, char):
		if len(char) > 0:
			self.label(edit, char)
		else:
			self.unlabel(edit)

	def label(self, edit, char):
		global words # :\
		# TODO One letter labels closer to current position
		# Searches for all words with given regexp in current view and labels them
		# Contain words regions, so we can use entire region, or just one position
		hints = []
		# Find words in this region
		visible_region = self.view.visible_region()
		next_search = visible_region.begin()
		last_search = visible_region.end()
		# label A is nr 1, not 0
		index = 1
		words = []
		#self.edit = self.view.begin_edit(self.view, "AceJumpHints")

		while next_search < last_search:
			# find_all searches in entire file and we don't want this
			# Escape special characters, you can search them too!
			word = self.view.find(selection_regex.format(char), next_search)
			if word:
				words.append(word)
				label = number_to_letters(index)
				label_length = len(label)
				hint_region = sublime.Region( word.begin(), word.begin() + label_length)
				# Don't replace line ending with label
				if label_length > 1 and match(r'$', self.view.substr(word.begin() + label_length - 1)):
					replace_region = sublime.Region(word.begin(), word.begin() + 1)
					# print "not replacing line ending", label
				else:
					replace_region = hint_region
				self.view.replace(edit, replace_region, label)
				hints.append(hint_region)
				index += 1
				# print index, label
			else:
				# print "no words left", next_search, last_search
				break
			next_search = word.end()
		# print "no search area left", next_search, last_search
		matches = len(words)
		if not matches:
			self.view.set_status("AceJump", "No matches found")
			return
		# Which scope to use here, string?
		# comment, string
		self.view.add_regions("AceJumpHints", hints, "string")
		self.view.add_regions("AceJumpWords", words, "comment") # Will be: Enable with settings
		self.view.set_status(
			"AceJump", "Found {} match{} for character {}".format(matches, "es" if matches > 1 else "", char)
		)

	def unlabel(self, edit):
		# Erase hints and undo labels
		self.labels = False
		self.view.erase_regions("AceJumpHints")
		self.view.erase_regions("AceJumpWords")
		self.view.end_edit(edit)
		self.view.run_command("undo")


class JumpToRegionCommand(sublime_plugin.TextCommand):

	def run(self, edit, start, end):
		# Checking? try/except
		#region = sublime.Region(long(start), long(end))
		region = sublime.Region(start, end)
		if not region:
			print("JumpToRegion: Bad region!")
			return
		self.view.sel().clear()
		self.view.sel().add(region)
		self.view.show(region)


class JumpToPlaceCommand(sublime_plugin.TextCommand):

	def run(self, edit, start):
		# Should I do checking for correct number?
		self.view.sel().clear()
		#self.view.sel().add(sublime.Region(long(start)))
		self.view.sel().add(sublime.Region(start))
		#self.view.show(long(start))
		self.view.show(start)
