from modelscope import snapshot_download, AutoTokenizer, AutoModelForCausalLM
import torch

def load_agent_model():
    model_dir = snapshot_download("Shanghai_AI_Laboratory/internlm2-chat-7b-sft")
    tokenizer = AutoTokenizer.from_pretrained(model_dir, device_map="mps",
                                              trust_remote_code=True,
                                              torch_dtype=torch.float16)

    # Set `torch_dtype=torc h.float16` to load model in float16, otherwise it will be loaded as
    # float32 and might cause OOM Error.

    model = AutoModelForCausalLM.from_pretrained(model_dir,
                                                 device_map="mps",
                                                 trust_remote_code=True,
                                                 torch_dtype=torch.float16)
    return tokenizer, model



def init_agent(tokenizer, model):
    model = model.eval()
    length = 0
    for response, history in model.stream_chat(tokenizer,
                                               "你现在要参加一个狼人杀游戏。游戏规则如下：游戏分为白天与夜晚"
                                               "夜晚行动：狼人选择一个平民杀死。如果狼人成功杀死平民，游戏继续；"
                                               "如果狼人被投票杀死，游戏结束。"
                                               "白天行动：所有存活玩家（包括狼人）"
                                               "参与投票，决定白天处死的玩家。被投票数最多的玩家被处死，如果票数"
                                               "相同，则随机选择一名票数最高的玩家处死。",
                                               history=[]):
        # 流式获得agent输出
        print(response[length:], flush=True, end="")
        length = len(response)
    return response, history, length




