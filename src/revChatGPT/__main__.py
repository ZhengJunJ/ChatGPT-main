import json
import textwrap
from os.path import exists
from os import getenv
from sys import argv, exit

from revChatGPT import Chatbot
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
    "session_token": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..sg9Z_mBu9Isrl1za.Png2n2LlQeMVQGZOEMNsACO6O-GeJuq0Fb_UjcanlF89Pdm9SYzUVD9g50IIctH6Q4Xz1pvEJkbzu8ImI_woXqm-PH2gP9Sgw4XRElckuVapl6Kf8D3EpMNsPLPY2Br0DBRMJDQgxYOJYW6S-jjYDDoJXNgep1mSSvunX7vQyDimoA7qkSdXxJWHq0eAWZBBudTLFAGk8XmNkuTrSfX8_ZH5IaoUT6TiBbbSGFkvX5GY-EBmnTQIeMZGKElu4pMGpoKconPL8zgSfPOIkcGVBc0DNzazvhVNjMtZy_4RjuT0WuufxHjNYLoAT2UIAokOOmLGS6IzP3W3cg5d01jSjew9iQSAhmON1qSg1Zwrah-ndrfeZDyadvBDyHCWwWG0DEsYBnp9zXXlk-7mEexnzHVgf4TwIC06BAWDN4yL2bwtAFAqNjtmyICo9AS9kYxP1Sbu8H2hoAAsiBa4t6-m7_DnRRA92F6uYT8TDRhN8mOhEdb9XhrmOhTbaalUe-YFMPrLBbCu92bU05_y_Ph_2jCfBXDIsn99dHu29-HKXunOp2uvZK50X1h9z_Cv7jLlLrH7A8MEOpZBmGGell37cpeUwTN1-11mqgopEvmDKIccTHt_cfnaIl3CJ4PHtvVvA4a_wO6I3ElUfpj7ojayYaAh7uoBtDz2BWhkOnNc4pVLYgpdRShwE2ELg87Gu1L06p0Ioo8uMUZijndiv2hx6ZK1w9P3vvS-nT-uRtVW6CtjjCfNbUoftmu6fgLw_psEoVOCWrgTpEhDZzgSMY1dKhx-B4hK9X-eI-ecxx-yQQ0ABYehnwy7g64jOKVTl5gISX21MPdNJFKSB4T44RauIteqVf12v5spBv2AAWTi7enFwzjUhMiYW4CyxChT9Y9puOFBtCSlOCZO9T7YXaWeqTBfzrKmBGtrl758_MLRcbDwPFGvI52gHi9POD5kg5LUn4qxSHT-E7uAKivNLf4ZrFSbDHclKoML901rbr7cFYRV5y7sfy-G8PKJAf3VNT2xYa-EFZSScl6aBDwPoBHab5riBXGy8y4am_1La53ZJz0SgifFLE696weakCKtWmGZRIV6VFUGry0153G90BKP8F5mMhDDgwFmphZyJA79Bh_GedNvENZm7rrPLqPjonnrUqRq-qR6ZkTU-JVGOcpz-9VxW7fZDptNuSQbjOOFNlWJGWCYIFt7slMVgeJbjUW8bESXYEgvj-Uey7zMHHoDd33Vlupz9PQpkW2UQNibA01QMlfUnWEGBDYmDvWhMQdcoHvLnaNOFu_q70x9vV3JawyLl100pOWvZH2isDHDtbQrD9_NXIBu8OdPnzwT_zdbwTiROjDVLtJLoRDSzRT91E6PhzMy5n8kbS2psiHH9d2cFxzpS7wuprg-jiZLnCha4rAa5K1eZt4kZKyiER7Txf97FWKnAnTmrfaftw4tuQheuAOFIAYhhyX1Z-kFd3Q0d3o_ELkE9N8JnRk_X1s3hWVDR92nl60UoifSM7xuzSd6VmWK7f_yMw9vkoHXFRa7RxICDl2_J4U-NONdk7Ncu3qHY0ka2T25A5Qe-ccC3G6X7hl9PdjAnxHldlj4GKC9MZ6GmNRQ08o-yvF_GdqfkOZcGwiO1oSsV3swHWbsPU3deKlA3j2XNs2-RNjnuTjHhTZbvhW_MPACLnn-ENILxnIwexyvwh6DbjaisvRth8XKUvqIxmNtuTCSllJvqFUxddOViEaZut2exceHotxGqFITtOhimO2xFLMx_lX3UxQrdUfNAAdGhV9PSgEH2JRzYfVeXttVFbu3XlgrO0vh6OmmaxqQvvb_rsSj7pbnwHsUEowJBeZbSxtPDJj9apBELosx7l41rQpHYIlJ3UktPKOShWrb1TEEThvfwJo4-uJQvp2pGHNS5r88S-8ZhQPaloAdgFik1K49y55lLOZ59jrdw1t-Ix5O1GnegV1d58JkLVGmsVNILTeb8FvSctDdsRdMnMgrWBC10O71xxvFmgB4rtacnNQmSyGlIg2-WQ2wShNATxVBvDu1jhuqaFRM8UKY28UTcAq7BWGrZwEekjkstd698KTS1EZA5UDJT66uWbMalK5WU06-cy1_ScGyP_60Lku9aA_42R4MNKtLRZTaACsT8YgE9Mxhs6g3Su28wkRStg8by4xmbJZliNI6mWtpA-YYI3Jfj-BDTSuyhFiyv_BcNYyh7-Ahffas3KpPKjKJqfvkD6eoG3m91ADS7FISGfX3jz3W-7io_L49cjG-NIFvvGY5Ah2B2-hMRKCn0Pi6fTvNXD07bXvTQNsL0zKkcYTD31ldeTiZsLWRmJqwsa4jqIJHXLBRy0rD46XHxulPj3ix4wQ.joY7YtZTbMcoQGeMW9k2lA",
    "cf_clearance": "ys5CMGahCEsrR8bBYVKYG6buvJGdwWCkePhYH.6NTeQ-1670830003-0-160",
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
}

hello_chatbot = Chatbot(config, conversation_id=None)


class MainHandler(tornado.web.RequestHandler):

    def __init__(self, *argc, **argkw):
        super(MainHandler, self).__init__(*argc, **argkw)

    # 解决跨域问题
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")  # 这个地方可以写域名
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.set_header("Access-Control-Max-Age", 1000)
        self.set_header("Content-type", "application/json")

    def get(self):
        question = self.get_argument('question')
        response = hello_chatbot.get_chat_response(str(question), output="stream")
        for res in response:
            self.write("response=" + str(res))

    def post(self):
        # post请求
        body = self.request.body
        body_decode = body.decode()
        body_json = json.loads(body_decode)
        question = body_json.get("question")
        response = hello_chatbot.get_chat_response(str(question), output="stream")
        for res in response:
            self.write("response=" + str(res))


application = tornado.web.Application([(r"/chat", MainHandler), ])

if __name__ == "__main__":
    application.listen(8848)
    tornado.ioloop.IOLoop.instance().start()
