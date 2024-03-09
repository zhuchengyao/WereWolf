import pygame
import random
import utility
import Player_agent


# 定义玩家类
class Player:
    def __init__(self, role, number, tokenizer, model):
        self.role = role  # 角色：'werewolf' 或 'villager'
        self.alive = True
        self.tokenizer = tokenizer
        self.model = model
        self.response, self.history, self.length = self.init_agent()
        self.number = number

    def __lt__(self, other):
        return self.number < other.number



    def init_agent(self):
        model = self.model.eval()
        length = 0
        response = None
        history = None
        prompt = (f"你现在要参加一个狼人杀游戏。游戏规则如下：游戏分为白天与夜晚一共有4位玩家，1位狼人，"
                  "3位平民白天行动：所有存活玩家（包括狼人）进行一轮讨论，大家各自根据讨论结果参与投票，"
                  "决定白天处死的玩家。被投票数最多的玩家被处死，如果票数相同，则随机选择一名票数最高的玩"
                  "家处死。夜晚行动：狼人选择一个平民杀死。如果存活平民不为0，则游戏继续；如果狼人被投票"
                  "杀死，游戏结束。你的玩家编号是： {self.number}, 你的身份是: {self.role}"
                  "你所有的回答都要简短。如果听明白了就说'了解'")
        for response, history in model.stream_chat(self.tokenizer, prompt, history=[]):
            # 流式获得agent输出
            print(response[length:], flush=True, end="")
            length = len(response)
        return response, history, length


    #动画效果
    def character_say(self):
        pass


    def agent_statement(self, previous_info):
        model = self.model.eval()
        length = 0
        prompt = f"补充发言为:\n {previous_info}. \n请开始你的发言，注意发言要简短."
        response = None
        history = None
        for response, history in model.stream_chat(self.tokenizer, prompt, history=self.history):
            # 在屏幕上输出发言
            print(response[length:], flush=True, end="")
            length = len(response)

        # 更新history
        self.response = response
        self.history = history
        return response


    def agent_vote(self):
        # 获取agent投票结果并投票。
        model = self.model.eval()
        length = 0
        response = None
        history = None
        prompt = "请给出你的投票结果，选择你要投票的人的编号，格式如下：{vote: 1},仅仅返回投票结果即可。"
        for response, history in model.stream_chat(self.tokenizer, prompt, history=self.history):
            print(response[length:], flush=True, end="")
            length=len(response)
        pos = response.find('vote')
        len_response = len(response)
        if pos+6 < len_response and '0' < response[pos+6] < '9':
            return {self.number: response[pos+6]}




    def night_action(self):
        # 如果是狼人，获取agent选择结果，并投票
        pass


class Werewolf(Player):
    def __init__(self):
        self.alive = True

    def vote(self):
        pass

    def night_action(self):
        pass


class Villager(Player):
    def __init__(self):
        self.alive = True

    def vote(self):
        pass






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
players = ([Player('werewolf', werewolf_num, tokenizer, model)] +
           [Player('villager', villager_num, tokenizer, model) for villager_num in villagers_list])
players.sort()

# 游戏主循环
running = True
day_time = True  # True 表示白天，False 表示夜晚
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))  # 清屏

    if day_time:
        # 各自发言环节
        info_pool = []
        for i, player in enumerate(players):
            # chat(previous_info)
            if not player.alive:
                continue

            if i == 1:
                previous_info = None
                response = player.agent_statement(previous_info)
                info_pool.append(response)
            else:
                previous_info = None
                for his_num, his_info in enumerate(info_pool, start=1):
                    previous_info = f"{his_num}号玩家发言: " + his_info + '\n '
                response = player.agent_statement(previous_info)

        # 投票环节
        for i, player in enumerate(players):
            player.vote()

        # 结算投票
        votes = {p: 0 for p in players if p.alive}
        for p in players:
            if p.alive:
                voted = p.vote(players)
                votes[voted] += 1

        # 处理投票结果
        max_votes = max(votes.values())
        for p, v in votes.items():
            if v == max_votes:
                p.alive = False
                break

        day = False  # 切换到夜晚
    else:
        # 夜晚逻辑：狼人行动
        for p in players:
            if p.alive and p.role == 'wolf':
                victim = p.night_action(players)
                if victim:
                    victim.alive = False
                    break

        day = True  # 切换到白天

    # 检查游戏结束条件
    if not any(p.alive and p.role == 'wolf' for p in players) or \
            not any(p.alive and p.role == 'villager' for p in players):
        running = False

    # 更新屏幕
    pygame.display.flip()
    pygame.time.delay(1000)  # 延迟以便观察

pygame.quit()
