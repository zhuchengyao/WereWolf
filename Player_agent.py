import random
from modelscope import snapshot_download, AutoTokenizer, AutoModelForCausalLM
import torch
from transformers import BitsAndBytesConfig
import utility


def load_agent_model():
    model_dir = snapshot_download("Shanghai_AI_Laboratory/internlm2-chat-20b-sft")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16
    )
    tokenizer = AutoTokenizer.from_pretrained(model_dir, device_map="cuda",
                                              trust_remote_code=True,
                                              load_in_4bit=True)

    # Set `torch_dtype=torc h.float16` to load model in float16, otherwise it will be loaded as
    # float32 and might cause OOM Error.

    # model = AutoModelForCausalLM.from_pretrained(model_dir,
    #                                              device_map="cuda",
    #                                              trust_remote_code=True,
    #                                              torch_dtype=torch.float16)
    model = AutoModelForCausalLM.from_pretrained(model_dir, device_map="auto", trust_remote_code=True,
                                                 quantization_config=bnb_config)
    return tokenizer, model


def init_agent(tokenizer, model):
    model = model.eval()
    length = 0
    response = None
    history = None
    for response, history in model.stream_chat(tokenizer,
                                               "",
                                               history=[]):
        # 流式获得agent输出
        print(response[length:], flush=True, end="")
        length = len(response)
    return response, history, length


# 定义玩家类
class Player:
    def __init__(self, role, number, tokenizer, model):
        self.role = role  # 角色：'werewolf' 或 'villager'
        self.alive = True
        self.tokenizer = tokenizer
        self.model = model
        self.number = number
        self.response, self.history, self.length = self.init_agent()

    def __lt__(self, other):
        return self.number < other.number

    def init_agent(self):
        model = self.model.eval()
        length = 0
        response = None
        history = None
        prompt = ("你现在要参加一个狼人杀游戏。游戏规则如下：游戏分为白天与夜晚一共有4位玩家，1位狼人，"
                  "3位平民白天行动：所有存活玩家（包括狼人）进行一轮讨论，大家各自根据讨论结果参与投票，投票只能投给目前存活的玩家"
                  "决定白天处死的玩家。被投票数最多的玩家被处死，如果票数相同，则随机选择一名票数最高的玩"
                  "家处死。夜晚行动：狼人选择一个平民杀死。如果存活平民不为0，则游戏继续；如果狼人被投票"
                  f"杀死，游戏结束。你的玩家编号是： {self.number}, 你的身份是: {self.role}，如果你是平民，请努力找出狼人，如果你是"
                  f"狼人，请隐藏自己并且努力获得胜利.尽力活到最后。。"
                  "如果听明白了就说'了解'")
        for response, history in model.stream_chat(self.tokenizer, prompt, history=[]):
            # 流式获得agent输出
            print(response[length:], flush=True, end="")
            length = len(response)
        return response, history, length

    # 动画效果
    def character_say(self):
        pass

    def agent_statement(self, previous_info):
        model = self.model.eval()
        length = 0
        prompt = f"你前面的玩家发言为:\n {previous_info}. \n请你作为{self.number}号玩家开始发言."
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

    def agent_vote(self, post_info, alive_info):
        # 获取agent投票结果并投票。
        model = self.model.eval()
        length = 0
        response = None
        history = None

        prompt = (f"你之后的玩家发言为:\n {post_info}. \n 请根据自己的身份请给出你的投票结果，选择一个目前还存活的人进行投票. \n"
                  + alive_info +
                  "例如你想要投票给2号，则:{vote: 2}，如果想要投弃权票，则投0，"
                  "例如，你想放弃，则返回:{vote: 1},投票的格式必须是:{vote: 4}类型。仅返回投票结果即可。")
        for response, history in model.stream_chat(self.tokenizer, prompt, history=self.history):
            print(response[length:], flush=True, end="")
            length = len(response)
        self.response = response
        self.history = history
        vote_pos = response.find('vote')
        if vote_pos == -1:
            vote_pos = response.find('投票给')
            if vote_pos != -1:
                vote_pos += 3
        else:
            vote_pos = vote_pos + 6
        len_response = len(response)
        if vote_pos == -1:
            return {self.number: int(0)}, 0
        if vote_pos < len_response and '0' <= response[vote_pos ] < '9':
            return {self.number: int(response[vote_pos])}, int(response[vote_pos])

    def agent_kill(self, day_night_message, alive_info):
        model = self.model.eval()
        length = 0
        response = None
        history = None
        prompt = day_night_message + ("目前是夜晚时间，请你选择你要杀死的对象"
                                      + alive_info +
                                      "你应该返回的结果格式样例如下:{kill: 4}, 仅返回杀死对象结果.")
        for response, history in model.stream_chat(self.tokenizer, prompt, history=self.history):
            print(response[length:], flush=True, end="")
            length = len(response)
        self.response = response
        self.history = history
        kill_pos = response.find('kill')
        if kill_pos == -1:
            kill_pos = response.find("杀死")
            if kill_pos != -1:
                kill_pos += 2
        else:
            kill_pos += 6
        len_response = len(response)
        if kill_pos < len_response and '0' <= response[kill_pos] < '9':
            return int(response[kill_pos])

    def agent_update(self, day_night_message):
        model = self.model.eval()
        length = 0
        response = None
        history = None
        prompt = "现在播报发生的事情：" + day_night_message + "了解了这些最新情况就回答:了解"
        for response, history in model.stream_chat(self.tokenizer, prompt, history=self.history):
            print(response[length:], flush=True, end="")
            length = len(response)
        self.response = response
        self.history = history


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
        return 0
    elif ALIVE_VILLAGER == 0:
        print("游戏介绍，狼人获胜")
        return 0
    return 1


def init_players(tokenizer, model):
    werewolf_num, villagers_list = utility.random_character(4, 1)
    # 创建玩家并排序
    number_of_players = 4
    players = ([Player('werewolf', werewolf_num, tokenizer, model)] +
               [Player('villager', villager_num, tokenizer, model) for villager_num in villagers_list])
    players.sort()
    return players


def werewolf_game_loop(players):
    while True:
        day_time = True
        day_night_message = ""
        number_of_players = len(players)
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
            game_continue = check_game_continue(players)
            if not game_continue:
                break
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
            game_continue = check_game_continue(players)
            if not game_continue:
                break
            day_time = True  # 切换到白天
