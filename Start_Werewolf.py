import pygame
import random
import utility
import Player_agent
import string
from Player_agent import Player,werewolf_game_loop
import threading
import queue

if __name__=="__main__":
    # 初始化AI模块
    tokenizer, model = Player_agent.load_agent_model()
    players = Player_agent.init_players(tokenizer, model)

    ALIVE_WEREWOLF = 1
    ALIVE_VILLAGER = 3

    # 游戏主循环
    running = True
    day_time = True  # True 表示白天，False 表示夜晚

    # 初始化Pygamea
    pygame.init()
    screen_width = 1080
    screen_hight = 768
    # 其他设置
    screen = pygame.display.set_mode((screen_hight, screen_hight))
    backgroundImage = pygame.image.load('./materials/background/summer_sunset.jpg')
    pygame.display.set_caption('狼人杀 - 简化AI版')
    t1 = threading.Thread(target=werewolf_game_loop, args=(players,))
    t1.start()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(backgroundImage, (0, 0)) # 清屏
        # 更新屏幕
        pygame.display.flip()
        pygame.time.delay(1000)  # 延迟以便观察

    pygame.quit()
