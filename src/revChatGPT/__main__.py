import json
import textwrap
from os.path import exists
from os import getenv
from sys import argv, exit
from typing import Optional, Awaitable

from revChatGPT import Chatbot, AsyncChatbot
import tornado.ioloop
import tornado.web
import json

class CaptchaSolver:
    """
    Captcha solver
    """
    @staticmethod
    def solve_captcha(raw_svg):
        """
        Solves the captcha

        :param raw_svg: The raw SVG
        :type raw_svg: :obj:`str`

        :return: The solution
        :rtype: :obj:`str`
        """
        # Get the SVG
        svg = raw_svg
        # Save the SVG
        print("Saved captcha.svg")
        with open("captcha.svg", "w", encoding='utf-8') as f:
            f.write(svg)
        # Get input
        solution = input("Please solve the captcha: ")
        # Return the solution
        return solution


def get_input(prompt):
    # prompt for input
    lines = []
    print(prompt, end="")
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    # Join the lines, separated by newlines, and print the result
    user_input = "\n".join(lines)
    # print(user_input)
    return user_input


def main():
    if "--help" in argv:
        print(
            """
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        Run with --debug to enable debugging
        """,
        )
        exit()
    try:
        print(
            """
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        Run with --debug to enable debugging
        """,
        )
        print("Type '!help' to show commands")
        print("Press enter twice to submit your question.\n")

        config_files = ["config.json"]
        xdg_config_home = getenv("XDG_CONFIG_HOME")
        if xdg_config_home:
            config_files.append(f"{xdg_config_home}/revChatGPT/config.json")
        user_home = getenv("HOME")
        if user_home:
            config_files.append(f"{user_home}/.config/revChatGPT/config.json")

        config_file = next((f for f in config_files if exists(f)), None)
        if not config_file:
            print("Please create and populate ./config.json, $XDG_CONFIG_HOME/revChatGPT/config.json, or ~/.config/revChatGPT/config.json to continue")
            exit()

        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)
        if "--debug" in argv:
            print("Debugging enabled.")
            debug = True
        else:
            debug = False
        print("Logging in...")
        chatbot = Chatbot(config, debug=debug,
                          captcha_solver=CaptchaSolver())

        while True:
            prompt = get_input("\nYou:\n")
            if prompt.startswith("!"):
                if prompt == "!help":
                    print(
                        """
                    !help - Show this message
                    !reset - Forget the current conversation
                    !refresh - Refresh the session authentication
                    !rollback <num> - Rollback the conversation by <num> message(s); <num> is optional, defaults to 1
                    !config - Show the current configuration
                    !exit - Exit the program
                    """,
                    )
                    continue
                elif prompt == "!reset":
                    chatbot.reset_chat()
                    print("Chat session reset.")
                    continue
                elif prompt == "!refresh":
                    chatbot.refresh_session()
                    print("Session refreshed.\n")
                    continue
                # elif prompt == "!rollback":
                elif prompt.startswith("!rollback"):
                    try:
                        num = int(prompt.split(" ")[1])  # Get the number of messages to rollback
                    except IndexError:
                        num = 1
                    chatbot.rollback_conversation(num)
                    print(f"Chat session rolled back {num} message(s).")
                    continue
                elif prompt == "!config":
                    print(json.dumps(config, indent=4))
                    continue
                elif prompt == "!exit":
                    break

            if "--text" not in argv:
                lines_printed = 0

                try:
                    print("Chatbot: ")
                    formatted_parts = []
                    for message in chatbot.get_chat_response(prompt, output="stream"):
                        # Split the message by newlines
                        message_parts = message["message"].split("\n")

                        # Wrap each part separately
                        formatted_parts = []
                        for part in message_parts:
                            formatted_parts.extend(
                                textwrap.wrap(part, width=80))
                            for _ in formatted_parts:
                                if len(formatted_parts) > lines_printed + 1:
                                    print(formatted_parts[lines_printed])
                                    lines_printed += 1
                    print(formatted_parts[lines_printed])
                except Exception as exc:
                    print("Response not in correct format!")
                    print(exc)
                    continue
            else:
                try:
                    print("Chatbot: ")
                    message = chatbot.get_chat_response(prompt)
                    print(message["message"])
                except Exception as exc:
                    print("Something went wrong!")
                    print(exc)
                    continue
    except KeyboardInterrupt:
        print("\nGoodbye!")
        exit()
    except Exception as exc:
        print("Something went wrong! Please run with --debug to see the error.")
        print(exc)
        exit()


config = {
    "session_token": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..TExOHAKdkGtlR619.2h5ggoQflF_NwBAwcNK3iIEvPMXTrEdwB0TzLp1FyKUYydcNKT32Ro0Q0-nRUV-Dx8KXDDIHp6oHKO5QIxgDqmhLmvv90m4UDM3CfS3pQnUBufDq7wu4jQVgYj9FdpzN1EgsxqyNLouYjvKEpooePjh1ZCzOzOcsU50l82vi0V_F89vCPQ25A5blNbDzF_enkXpDhG-H3p0WHKMnq3GVugKPrv_25vJTBxZjhavxHpySRGFl7UfScqUdbCy1kzmolSzKld0eBOhc98_O1YSjgADQfeYGvt6L-uPSSULv9TTTkCJInfMCA__o0QT1fDpcgNXRSNl4sAaro9jmNxhI1ZOlsdd1tZ3IR3S-55Nnm_VGEr9fnGrK5OShhtrFt2m2HfmQk5Av6RQWWSFTnu0hN8lKWWPV3PKIsUVKZGQBXSHbLHFYqBqN06b5t7noXNT0LmuLr0DIXgy0KpPgheTImdbGUG_Mk6RQLlfRKsNRDio8DqRpQQthlhQy18ZqibrX2rGJJLZBoMkv1HWQmjWT78UKGs2-X-rPRVW23XR63zgEKQVi1098VcFLvp7zk0cQi8WMmweWNDZs-otN2TL_pkxhgPvjmL3Z7wlvxV38JLuwSTYsxp7mxeI9r5iAeAD3L2mSn8-BnKqaVpGgTI3T_LjnSNytyiGCXQaGzv0cGBZ9IGHjfMNiX1Fm-lGoHodhZ11KVmCjAepIivWoEmPwAzW1BDXqs3j4StjQ6LQECrD9DvEMLh00Pco-1aYywjtEhb-UAIvDiKSiDPUyjAA5Y22yuVlZ5hu7wC2yQDtTisATayY2GHX7Cd7xYt20Ptw0mwoEeDRliMxbT8813Yg90_c9lQtkXiHcH_76-Zrqy2Pi_VoW9dBXATL8z9x9lsDWktXtSMOknbcg4ZeDeIHbZIfQ8KNqdlchdzXWbZuqj1P0WwWGFCFq65_LH8_sN8GjyTaj-bdi9eCabBBgSBdVAJBLJYiuDUEMKasOFxyRODAXcZKaGxjplAGBWH6ucoJk1kfyK4gyC1eOCYp3BGNvn9yweaZtpKEZ56nZUabHMSJdHm4wpvUvU3BQvbh9TSXZYT9_VGIfM3CLMCDBWPjFS6QgCeAzPzGxfmZ0XyN_UrQrJGxBoRXLLOYItHZqjG_gaJh7jMay_icFNu8UTqCeh8vx3JTplE1Mqcffccu0n7x4nXKwz0Y2g2SxapHZbLsL_oh6alJ-YXkbNuAoyork9fsp_BJQgPSmeUd-jYgm4WpuFsBbOyf5XFcmmq37Em16weXMoFqhNXFvvZgJ97kCYM_QsvMngaHGOF20_J3kGc5uV4QoIPC2BzevRGijG5MvsLnXD54vQYqb0mwXyixp8DRI16oZszwWTD7fW5jr0KHXEzEYcROLbubND9LGPwPWb3P8l2INTYgic4EvsSjVHPhSfpRDq7YbL84Ez9_YCoGp-WPzrNF9FTDMhP7AxfBl7r0ButWhBIY-vKJv3qFV02DpPtFSCEQlDnOtJmil_C4xnkP5FcbRDb8GKkOvvYhfEpUtSt6B_49N_6USz58tBJHc78zCdlDR57WnX1QDNPS4XA6gE0aLyV5N-75KaPPcoKbTj4sAXAPCmv6vlYUv5daP9o1GIt7d4y2isxjhl1DAARXoTp6hG4sAX-msMFzlO0sgAOmo7RB38m5gH_AUuJY7djVslRPQgzwjKg9JsRhXqRVjxGB0BuxkWoF7_bvgzs8xPngCXSMqN_oY1iccNZqCiAvO5SD3fvveVrtViQtvsZuIGO3GLRap4_2WGPaJC919I9DjCqL26mhDvd4e6RgiUC6O3vk12vnveChS0rOOIwpG4uqR9sw1wmTXxoXTwqbi2JQNWuGKqkg-U8m1g8zzeqnBcjzBekgdPyuia_SvM6F8hzV6NbRJDoM11KB414FHDTisV81GeKvuETg-z7ZZUI2gq2s4w37p-5llQa61NOzEiTsPASwGAuHqoESRmtnC6SMKNu4vqw4LkF8Ip2sO8ON1Ifzr6MScjc_AbXFlOjoTrnkL9Dkm_VQpxSkN_O5WN_69dQHgKacWOvJOMYTg1X_UB3dfbwSJRZEFHfeYYZ3Jpip8tbAOezYIasaBR8I0eE9jMJAwzCzhcPim4wgCQARwVEGeCbyttdKpLJWs6XmYeaNsMpDMwttXnWVxS2ObwhS1mLKVQdIWUZtXlDLNWD_Pb5rn-oPA11ZTni5NMBsA4j_h4mpvsi67k-LI5z7yuK4acbNytPLKgK73dsN_tNy0CS77WmFueQYFgJpvbWx8uX606IOLQMtlgqHV86yHJ4WuE71vtRAV3S677L09bVNIvzaxLsfnj_Z0esvyL2QlXCAdxeA.h4tYY9_RB3tXNpZHdZzCdQ",
    "cf_clearance": "KVyyuOmDiLchRtD.ZQi1kbqWKq50kQJdlW.SgpB9D34-1670897662-0-1-436a96b4.1823a3a6.146bc954-160",
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
}



hello_chatbot = AsyncChatbot(config, conversation_id=None)


class MainHandler(tornado.web.RequestHandler):

    def __init__(self, *argc, **argkw):
        super(MainHandler, self).__init__(*argc, **argkw)

    def options(self):
        print("域检请求通过")
        # 跨域options请求 直接返回ok
        self.set_status(204)
        self.finish()

    # 解决跨域问题
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", self.request.headers.get("Origin", "*"))
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.set_header("Access-Control-Max-Age", 1000)
        self.set_header("Content-type", "application/json")

    async def get(self):
        # get 请求
        question = self.get_argument('question')
        print(question)
        '''response = hello_chatbot.get_chat_response(str(question), output="stream")
        result = None
        for res in response:
            result = res
        result_json = json.dumps(result)
        # print(result_json)
        self.write(result_json)'''
        self.set_header('Content-Type', 'text/event-stream; charset=utf-8')
        # self.set_header('Transfer-Encoding', 'chunked')
        self.set_header('Connection', 'keep-alive')

        async for i in await hello_chatbot.get_chat_response(question, output="stream"):
            print(i['message'])
            self.write(i['message'])
            self.flush()
        self.finish()

    async def post(self):
        # post 请求
        body = self.request.body
        body_decode = body.decode()
        body_json = json.loads(body_decode)
        question = body_json.get("question")
        self.set_header('Content-Type', 'text/event-stream; charset=utf-8')
        # self.set_header('Transfer-Encoding', 'chunked')
        self.set_header('Connection', 'keep-alive')
        async for i in await hello_chatbot.get_chat_response(question, output="stream"):
            print(i['message'])
            self.write(i['message'])
            self.flush()
        self.finish()
        '''response = hello_chatbot.get_chat_response(str(question), output="stream")
        result = None
        for res in response:
            result = res
        result_json = json.dumps(result)
        # print(result_json)
        self.write(result_json)'''




application = tornado.web.Application([(r"/chat", MainHandler), ])

if __name__ == "__main__":
    application.listen(8848)
    tornado.ioloop.IOLoop.instance().start()
