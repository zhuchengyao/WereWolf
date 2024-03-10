import pygame
import random
import utility
import Player_agent
import string
from Player_agent import Player


# 初始化Pygame
pygame.init()

# 初始化AI模块
tokenizer, model = Player_agent.load_agent_model()

# 其他设置
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('狼人杀 - 简化AI版')

# 确定随机的狼人和平民编号, 4位总玩家数， 1为狼人数量
werewolf_num, villagers_list = utility.random_character(4, 1)

# 创建玩家并排序
number_of_players = 4
players = ([Player('werewolf', werewolf_num, tokenizer, model)] +
           [Player('villager', villager_num, tokenizer, model) for villager_num in villagers_list])
players.sort()
ALIVE_WEREWOLF = 1
ALIVE_VILLAGER = number_of_players-ALIVE_WEREWOLF

# 游戏主循环
running = True
day_time = True  # True 表示白天，False 表示夜晚





def check_game_continue(players):
    global ALIVE_WEREWOLF
    global ALIVE_VILLAGER
    alive_werewolf = 0
    alive_villager = 0
    for player in players:
        if player.alive:
            if player.role == "werewolf":
                alive_werewolf += 1
            elif player.role == "villager":
                alive_villager += 1
    ALIVE_VILLAGER = alive_villager
    ALIVE_WEREWOLF = alive_werewolf
    if ALIVE_WEREWOLF == 0:
        print("游戏结束，平民获胜")
        pygame.quit()
    elif ALIVE_VILLAGER == 0:
        print("游戏介绍，狼人获胜")
        pygame.quit()


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))  # 清屏
    day_night_message = ""

    #  白天逻辑
    if day_time:

        #  更新投票和夜晚的信息，第二天才开始
        if day_night_message:
            for player in players:
                if player.alive:
                    player.agent_update(day_night_message)

        # 存活玩家各自发言环节
        info_pool = []
        for i, player in enumerate(players):
            if not player.alive:
                continue
            previous_info = utility.previous_statement_generation(info_pool)
            response = player.agent_statement(previous_info)
            info_pool.append(response)

        # 投票环节
        vote_result = {}
        vote_result_message = ""
        for player_number, player in enumerate(players, start=1):
            if not player.alive:
                continue
            post_info = utility.post_statement_generation(info_pool, player_number)
            alive_info = utility.check_live(players)
            temp_result, _temp_result = player.agent_vote(post_info, alive_info)

            vote_result_message += f"{player_number}号投票给了{_temp_result}号玩家.\n"
            if temp_result is not None:
                vote_result.update(temp_result)

        # 结算投票,遍历vote_result里的value项,并得到结果，更新在Agent里。recipients_indices是得票最多player数，即平票最高有多少人
        vote_recipients, recipients_indices = utility.find_highest_votes(vote_result, number_of_players)
        finally_res = -1

        if recipients_indices == 1:  # 只有一个最高得票
            if vote_recipients[0] == 0:  # 得到最高票的是弃权票
                day_night_message = day_night_message + "弃权票获得最高票数，没有玩家被处死.\n"  # 需要从传递的信息添加
            else:  # 最高票是某个player
                finally_res = players[vote_recipients[0]-1].number
                players[vote_recipients[0]-1].alive = False
                day_night_message = day_night_message + f"被投票处死的是{finally_res}号玩家.\n"
        else:  # 多个的票平分最高
            executed_player = vote_recipients[random.randint(0, recipients_indices-1)]
            if(executed_player == 0):
                day_night_message = day_night_message + "随机到的并列最高票数结果为弃权票，没有玩家被处死.\n"
                print(day_night_message)
            else:
                players[executed_player-1].alive = False
                finally_res = players[executed_player-1].number
                day_night_message = day_night_message + f"被投票处死的是{finally_res}号玩家.\n"
                print(day_night_message)
        # 这里day_night_message把投票结保存，与狼人晚上的行动结果一起给到第二天的agents。

        # 检查游戏是否继续
        check_game_continue(players)
            # 画面另写

        day_time = False  # 切换到夜晚
    else:
        # 夜晚逻辑：狼人行动
        victim = -1
        alive_info = utility.check_live(players)
        for player in players:
            if player.alive and player.role == 'werewolf':  # 找到狼人角色
                victim = player.agent_kill(day_night_message, alive_info)
        for player in players:
            if player.alive and player.number == victim:
                player.alive = False
                day_night_message += f"夜晚被狼人杀死的玩家是{player.number}号玩家。\n"

        check_game_continue(players)

        day_time = True  # 切换到白天

    # 更新屏幕
    pygame.display.flip()
    pygame.time.delay(1000)  # 延迟以便观察

pygame.quit()
