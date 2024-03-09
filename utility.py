import random


# List of numbers to choose from
def random_character(total_player_number, werewolf_number):
    numbers = [i+1 for i in range(total_player_number)]

    # Use random.choice to select one number randomly
    selected_number = random.choice(numbers)

    # Remove the selected number from the list
    numbers.remove(selected_number)

    # return will be two elements, first is werewolf number, second is a list contains all villagers' number.
    return selected_number, numbers
