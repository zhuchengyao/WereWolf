import random


# List of numbers to choose from
def random_character(total_player_number, werewolf_number):
    numbers = [i + 1 for i in range(total_player_number)]
    # Use random.choice to select one number randomly
    selected_number = random.choice(numbers)
    # Remove the selected number from the list
    numbers.remove(selected_number)
    # return will be two elements, first is werewolf number, second is a list contains all villagers' number.
    return selected_number, numbers


def find_highest_votes(vote_result, number_of_players=4):
    roll = []
    for i in range(number_of_players + 1):
        roll.append(0)
    for key, value in vote_result.items():
        roll[value] = roll[value] + 1
    max_value = max(roll)
    max_indices = [index for index, value in enumerate(roll) if value == max_value]
    return max_indices, len(max_indices)


def previous_statement_generation(info_pool):
    previous_info = ""
    for his_num, his_info in enumerate(info_pool, start=1):
        previous_info += f"{his_num}号玩家的发言是: " + his_info + '\n '
    return previous_info


def post_statement_generation(info_pool, player_num):
    post_pool = info_pool[player_num:]
    start_num = player_num+1
    post_info = ""
    for his_info in post_pool:
        post_info += f"{start_num}号玩家的发言是: " + his_info + '\n '
        start_num += 1
    return post_info


def check_live(players):
    alive_list = []
    for player in players:
        if player.alive:
            alive_list.append(player.number)
    alive_message = "目前还存活的玩家有: "
    for alive_player in alive_list:
        alive_message += str(alive_player) + " "
    return alive_message


