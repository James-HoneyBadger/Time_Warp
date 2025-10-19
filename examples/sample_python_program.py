#!/usr/bin/env python3
"""
Python Text Adventure Game
This program demonstrates Python programming concepts including:
- Object-oriented programming
- Data structures (dictionaries, lists)
- Control flow (loops, conditionals)
- Functions and methods
- String manipulation
"""

import random
import sys


class Room:
    """Represents a room in the adventure game"""

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.exits = {}
        self.items = []
        self.visited = False

    def add_exit(self, direction, room):
        """Add an exit to another room"""
        self.exits[direction] = room

    def add_item(self, item):
        """Add an item to the room"""
        self.items.append(item)

    def remove_item(self, item):
        """Remove an item from the room"""
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def describe(self):
        """Describe the room to the player"""
        if not self.visited:
            print(f"\n=== {self.name} ===")
            print(self.description)
            self.visited = True
        else:
            print(f"\nYou are in {self.name}")

        if self.items:
            print("\nYou see:")
            for item in self.items:
                print(f"  - {item}")

        if self.exits:
            print("\nExits:")
            for direction in self.exits.keys():
                print(f"  - {direction}")


class Player:
    """Represents the player character"""

    def __init__(self, name):
        self.name = name
        self.inventory = []
        self.current_room = None
        self.health = 100
        self.score = 0

    def move(self, direction):
        """Move the player in a direction"""
        if direction in self.current_room.exits:
            self.current_room = self.current_room.exits[direction]
            self.score += 1
            return True
        else:
            print("You can't go that way!")
            return False

    def take_item(self, item):
        """Take an item from the current room"""
        if self.current_room.remove_item(item):
            self.inventory.append(item)
            print(f"You took the {item}")
            self.score += 5
            return True
        else:
            print(f"There's no {item} here!")
            return False

    def show_inventory(self):
        """Show the player's inventory"""
        if self.inventory:
            print("\nInventory:")
            for item in self.inventory:
                print(f"  - {item}")
        else:
            print("\nYour inventory is empty.")

    def show_status(self):
        """Show player status"""
        print(f"\nPlayer: {self.name}")
        print(f"Health: {self.health}")
        print(f"Score: {self.score}")


class AdventureGame:
    """Main game class"""

    def __init__(self):
        self.player = None
        self.rooms = {}
        self.game_over = False
        self.setup_world()

    def setup_world(self):
        """Create the game world"""
        # Create rooms
        entrance = Room(
            "Entrance Hall",
            "A grand entrance hall with marble floors and high ceilings. "
            "Sunlight streams through stained glass windows.",
        )

        library = Room(
            "Ancient Library",
            "Towering bookshelves filled with dusty tomes. "
            "The air smells of old parchment and wisdom.",
        )

        garden = Room(
            "Secret Garden",
            "A beautiful garden hidden behind the mansion. "
            "Colorful flowers bloom everywhere and a fountain gurgles peacefully.",
        )

        treasure_room = Room(
            "Treasure Chamber",
            "A mysterious chamber filled with glittering treasures. "
            "Golden coins and precious gems are scattered about.",
        )

        # Connect rooms
        entrance.add_exit("north", library)
        entrance.add_exit("east", garden)

        library.add_exit("south", entrance)
        library.add_exit("secret", treasure_room)

        garden.add_exit("west", entrance)

        treasure_room.add_exit("exit", library)

        # Add items
        library.add_item("ancient book")
        library.add_item("magic key")
        garden.add_item("beautiful flower")
        garden.add_item("silver coin")
        treasure_room.add_item("golden chalice")
        treasure_room.add_item("ruby necklace")

        # Store rooms
        self.rooms = {
            "entrance": entrance,
            "library": library,
            "garden": garden,
            "treasure": treasure_room,
        }

    def start_game(self):
        """Start the adventure game"""
        print("=" * 50)
        print("🏰 Welcome to the Python Text Adventure! 🏰")
        print("=" * 50)

        name = input("\nWhat is your name, brave adventurer? ")
        self.player = Player(name)
        self.player.current_room = self.rooms["entrance"]

        print(f"\nWelcome, {name}! Your adventure begins...")
        print("\nCommands: go <direction>, take <item>, inventory, status, help, quit")

        # Main game loop
        while not self.game_over:
            self.player.current_room.describe()
            self.process_command()

    def process_command(self):
        """Process player commands"""
        command = input("\n> ").lower().strip()

        if command == "quit" or command == "exit":
            self.game_over = True
            print(f"\nThanks for playing, {self.player.name}!")
            print(f"Final Score: {self.player.score}")

        elif command == "help":
            self.show_help()

        elif command == "inventory" or command == "inv":
            self.player.show_inventory()

        elif command == "status":
            self.player.show_status()

        elif command.startswith("go "):
            direction = command[3:]
            self.player.move(direction)

        elif command.startswith("take "):
            item = command[5:]
            self.player.take_item(item)

        elif command == "look":
            self.player.current_room.visited = False

        else:
            print(
                "I don't understand that command. Type 'help' for available commands."
            )

    def show_help(self):
        """Show available commands"""
        print("\nAvailable Commands:")
        print(
            "  go <direction>  - Move in a direction (north, south, east, west, etc.)"
        )
        print("  take <item>     - Pick up an item")
        print("  inventory       - Show your inventory")
        print("  status          - Show your status")
        print("  look            - Look around the current room again")
        print("  help            - Show this help message")
        print("  quit            - Exit the game")


def main():
    """Main function to run the game"""
    try:
        game = AdventureGame()
        game.start_game()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please report this bug!")


if __name__ == "__main__":
    main()
