# !/usr/bin/env python3
"""
==== No Bugs in code, just some Random Unexpected FEATURES ====
┌─────────────────────────────────────────────────────────────┐
│┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐│
││Esc│!1 │@2 │#3 │$4 │%5 │^6 │&7 │*8 │(9 │)0 │_- │+= │|\ │`~ ││
│├───┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴───┤│
││ Tab │ Q │ W │ E │ R │ T │ Y │ U │ I │ O │ P │{[ │}] │ BS  ││
│├─────┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴─────┤│
││ Ctrl │ A │ S │ D │ F │ G │ H │ J │ K │ L │: ;│" '│ Enter  ││
│├──────┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴────┬───┤│
││ Shift  │ Z │ X │ C │ V │ B │ N │ M │< ,│> .│? /│Shift │Fn ││
│└─────┬──┴┬──┴──┬┴───┴───┴───┴───┴───┴──┬┴───┴┬──┴┬─────┴───┘│
│      │Fn │ Alt │         Space         │ Alt │Win│   HHKB   │
│      └───┴─────┴───────────────────────┴─────┴───┘          │
└─────────────────────────────────────────────────────────────┘

利用 LLM 进行文本分类任务。

Author: pankeyu
Date: 2023/03/17
"""
from rich import print
from rich.console import Console
from transformers import AutoTokenizer, AutoModel


# 提供所有类别以及每个类别下的样例
class_examples = {
        '有车吗':'约玩',
        '谁带我一下':'约玩',
        '2或好吃刷四星':'约玩',
        '你们满了吗':'约玩',
        '还差人吗':'约玩',
        '厨房2蹲车车':'约玩',
        '4k宝麻1＝234':'约玩',
        '4k胚胎麻1＝234':'约玩',
        '蹲一个四星车车':'约玩',
        '宝宝练习麻3=':'约玩',
        '4星节庆或者开图3=1':'约玩',
        '有车嘛':'约玩',
        '1＝1':'约玩',
        '麻团有人呢':'约玩',
        '4.5k麻2等123':'约玩',
        '宝宝练习麻团3=':'约玩',
        '2=2四星/刷分来个优质主机':'约玩',
        '等个宝麻':'约玩',
        '那冲四星':'约玩',
        '冲5k麻2=14':'约玩',
        '冲5k麻3=1':'约玩',
        '有车吗👀':'约玩',
        '2四星':'约玩',
        '厨房2，过四星，3=1':'约玩',
        '2=2':'约玩',
        '4k胚胎麻2＝23':'约玩',
        '2刷四星3=1':'约玩',
        '3=1':'约玩',
        '有人做饭吗':'约玩',
        '想打四星':'约玩',
        '全都好吃开图':'约玩',
        '蹲':'约玩',
        '我在线蹲steam厨房2主线搭子':'约玩',
        'SW厨房2！！！':'约玩',
        '厨房2四星':'约玩',
        '2等2':'约玩',
        '有网好的厨房2车车🚗嘛':'约玩',
        '好吃刷分有无':'约玩',
        '有人玩吗，厨房2':'约玩',
        '有车车吗':'约玩',
        '现在有人玩吗？':'约玩',
        '蹲蹲一起主线的':'约玩',
        '主线开图2🟰2':'约玩',
        '1等全世界':'约玩',
        '二等全世界':'约玩',
        '持续蹲蹲':'约玩',
        '带带我':'约玩',
        '那继续3＝1':'约玩',
        '下午茶有嘛2=2[苦涩]':'约玩',
        '有厨2车车🚗不':'约玩',
    }


def init_prompts():
    """
    初始化前置prompt，便于模型做 incontext learning。
    """
    unknown = "不知道"
    class_list = list(set(class_examples.values()))
    class_list.append(unknown)
    pre_history = [
        (
            f'现在你是一个文本分类器，你需要按照要求将我给你的句子分类到：{class_list}类别中。不确定的都认为是 {unknown} ',
            f'好的。'
        )
    ]

    for exmpale,_type in class_examples.items():
        pre_history.append((f'"{exmpale}" 是 {class_list} 里的什么类别？', _type))

    pre_history.append((f' "jfapfa" 是 {class_list} 里的什么类别？', unknown))
    pre_history.append((f' "kjzhxc9087   23rha980" 是 {class_list} 里的什么类别？', unknown))
    pre_history.append((f' "podiafopi2u0r4iaud098avphn" 是 {class_list} 里的什么类别？', unknown))
    pre_history.append((f' "1214556413265415781231" 是 {class_list} 里的什么类别？', unknown))
    pre_history.append((f' "嘿嘿" 是 {class_list} 里的什么类别？', unknown))
    pre_history.append((f' "哈哈" 是 {class_list} 里的什么类别？', unknown))
    return {'class_list': class_list, 'pre_history': pre_history}


def inference(
        sentences: list,
        custom_settings: dict
    ):
    """
    推理函数。

    Args:
        sentences (List[str]): 待推理的句子。
        custom_settings (dict): 初始设定，包含人为给定的 few-shot example。
    """
    for sentence in sentences:
        with console.status("[bold bright_green] Model Inference..."):
            sentence_with_prompt = f' "{sentence}" 是 {custom_settings["class_list"]} 里的什么类别？'
            response, history = model.chat(tokenizer, sentence_with_prompt, history=custom_settings['pre_history'])
        print(f'>>> [bold bright_red]sentence: {sentence}')
        print(f'>>> [bold bright_green]inference answer: {response}')
        # print(history)


if __name__ == '__main__':
    console = Console()

    device = 'cuda:0'
    tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)
    model = AutoModel.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True).half()
    model.to(device)

    sentences = [
        "有人玩吗",
        "蹲个车车",
        "3=1",
        "1等全世界",
        "有车吗"
        "2四星",
        "fasdfoaqiuoe",
        "不知道",
        "哈哈",
        "110938109380-12938-",
    ]
    
    custom_settings = init_prompts()
    inference(
        sentences,
        custom_settings
    )