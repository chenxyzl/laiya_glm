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
from http.server import BaseHTTPRequestHandler, HTTPServer

unknown = "无意义"

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
        '好啊':f'{unknown}',
        '2=2四星/刷分来个优质主机':'约玩',
        '等个宝麻':'约玩',
        '那冲四星':'约玩',
        '冲5k麻2=14':'约玩',
        '哈哈':f'{unknown}',
        '冲5k麻3=1':'约玩',
        '有车吗👀':'约玩',
        '2四星':'约玩',
        '厨房2，过四星，3=1':'约玩',
        '2=2':'约玩',
        '嘿嘿':f'{unknown}',
        '4k胚胎麻2＝23':'约玩',
        '1214556413265415781231':f'{unknown}',
        '2刷四星3=1':'约玩',
        '3=1':'约玩',
        'podiafopi2u0r4iaud098avphn':f'{unknown}',
        '有人做饭吗':'约玩',
        '想打四星':'约玩',
        '全都好吃开图':'约玩',
        '蹲':'约玩',
        '我在线蹲steam厨房2主线搭子':'约玩',
        'SW厨房2！！！':'约玩',
        '厨房2四星':'约玩',
        'kjzhxc9087   23rha980':f'{unknown}',
        '2等2':'约玩',
        '有网好的厨房2车车🚗嘛':'约玩',
        '好吃刷分有无':'约玩',
        '有人玩吗，厨房2':'约玩',
        '有车车吗':'约玩',
        '现在有人玩吗？':'约玩',
        '蹲蹲一起主线的':'约玩',
        'jfapfa':f'{unknown}',
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
    class_list = list(set(class_examples.values()))
    pre_history = [
        (
            f'现在你是一个文本分类器，你需要按照要求将我给你的句子分类到：[{",".join(class_list)}] 类别中。不确定怎么分类的就分类到 {unknown} ',
            f'好的。'
        )
    ]

    for exmpale,_type in class_examples.items():
        pre_history.append((f'"{exmpale}" 是 [{",".join(class_list)}] 里的什么类别？'.replace("\'",""), _type))
    return {'class_list': class_list, 'pre_history': pre_history}


def inferenceStr(
        sentence: str,
        custom_settings: dict
    ):
    """
    推理函数。

    Args:
        sentences (List[str]): 待推理的句子。
        custom_settings (dict): 初始设定，包含人为给定的 few-shot example。
    """
    with console.status("[bold bright_green] Model Inference..."):
        sentence_with_prompt = f' "{sentence}" 是 [{",".join(custom_settings["class_list"])}] 里的什么类别？'
        response, history = model.chat(tokenizer, sentence_with_prompt, history=custom_settings['pre_history'],max_new_tokens=20480)
        print(f'>>> [bold bright_red]sentence_with_prompt: {sentence_with_prompt}')
        print(f'>>> [bold bright_green]inference answer: {response}')
        print(history)
    return response

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
            response, history = model.chat(tokenizer, sentence_with_prompt, history=custom_settings['pre_history'],max_new_tokens=20480)
        print(f'>>> [bold bright_red]sentence: {sentence}')
        print(f'>>> [bold bright_green]inference answer: {response}')
        # print(history)


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 获取请求内容长度
        content_length = int(self.headers.get('Content-Length', 0))

        # 读取请求数据
        request_data = self.rfile.read(content_length).decode('utf-8')

        # 设置响应头
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()

        response_data = inferenceStr(
            request_data,
            custom_settings
        )

        # 设置响应内容
        self.wfile.write(response_data.encode('utf-8'))


if __name__ == '__main__':
    console = Console()

    device = 'cuda:0'
    tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int8", trust_remote_code=True)
    model = AutoModel.from_pretrained("THUDM/chatglm-6b-int8", trust_remote_code=True).half()
    model.to(device)

    custom_settings = init_prompts()
    print(f'>>> [bold bright_red]custom_settings: {custom_settings}')

    # sentences = [
    #     "有人玩吗",
    #     "蹲个车车",
    #     "3=1",
    #     "1等全世界",
    #     "有车吗",
    #     "2四星",
    #     "fasdfoaqiuoe",
    #     "不知道",
    #     "哈哈",
    #     "110938109380-12938-",
    # ]
    
    
    # inference(
    #     sentences,
    #     custom_settings
    # )

    server_address = ('', 21000)
    httpd = HTTPServer(server_address, MyHTTPRequestHandler)
    print('Server is running at http://localhost:21000/')
    httpd.serve_forever()
