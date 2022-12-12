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
    "session_token": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..Iu0M7if5g7ufUVV6.dOUKL-FK6N_cBlGw4J6yBV_DNkSceyxuAN9InommWUJRd_Pd7aTQl9HOKDx31QnKahDLNlqEo9BTDAQLUMlf3FV-HL8yzLeyQoaXIDeBDBtXZi87Wz9MmEUYljAtmmp1yvJ6GKDWLBjGoFgq7STNfNGn-9Vw9pDSiLQFULInjjoqeiSBDrzxozx6HVHg2jODGXCG3_A9NIxVGWmvHyAlJQgpyjkFXgAAyCxgQA0iKWVQqg7Yi8vGzBLDyQ6UKs7C6tU3BzvK9I-U83ImoymO0980t0fqoTvVzz-zpU2fTEfk5No-eN0TyXkh1YLcaXcEw2esxGmcJPlNR9PgzGRKaiKkfbgazu0sIBVBdMgpj6VRbRTC9Fg-DJgAqb4aiQUmZ0TllQEMQDKKVNf6Jj3H-rFbAnZjI_FhKiYpDb1CEtke5VXgFMHRmAxEe36tiJNlQwil5CLeQQXjET1ydUrB7_kXFVRQam2vwF6zi3nuWrwv5gF7OfrlHn7J6XTkvduBTLw0ECTpNLfgi4vaUfKVT4_0J4Z-pX5itKNgVYwlVJexY8OJ1ebHu3R5rWqI2RNpbfcXGjhawu4fXSUwkWyHIMfZZdpQldDYkEuKKH_648eBNYynRrAn1fqwRYsKOBSAT4xxl4r4C9QMk9acQc9RtViKITnrPTbCdb0fYGyV2qwQ3Vc5c7ih7v66HTA-ixGTZrMyHECIytsKLHZcoJUiBtin6cE_r7N70gVGpOzKA_gkviZjVZkhi7fPMVERle9EqLUWWvC2ehBFSg_n8JOS1b1AWBe12QCDHmkDSLHd1KQKW4-zFPzmZSbfH8fUGjU5c0Sh3OZAMc-HcFa4JF9KcmqRqjpBV4-CCPS7yMj_ndzJCyDXOunsy_KCXaiGfKZfGWd9SovoOYaANM48KbNKBS44FCMxkztnyQXyHyQvxF7vMYCQUxP1CMmxYsWCvM6qAQmmqnoMiBEHDLGNjaDC5as_MvepqHo94aZW_CXUNBDppDEY0D8lFBm3MO-UtVUnmUlG71udQJ-RFVdgKcJ5w9EwHNn_3kPIyWdIVhub9DPJfNk3vkjCIaH5KkTcIWIIZukKsmoQvDKm36nvzg0WomvQUktKde52S47_32ebIwNLh6tfEX9QGQR4BqxSDO4v_BTLgBiK126i-_E_CnrzPE2aozI86QUWVs7-qGv4N5LJdI1Af4XJ5_cv7cW5tZ1217MwuCnD60_W8rCL2hxyOv_Gcs1buN1oMDEc43Xv2M1Zj87LXmnvxPXl10JxVl7E9miUfMKzCf_UsFvYX2zvqFYXuT1gonS3PHjjYQsi9fn61ExZNzooCzJdHFMXTVclgJa1uWJcrOSE9iN3tebJft3oX7bcQaDVU2E7wByKiglEdJR98NfxaiyuvpghJeM0ufNfnM66dYl9SwF0sJjYGDbn9uz8HMEyg_QG92e-Mqv7H2iW7T1eZmEfLTbfLxzuneGOiAEnEoyfwiqHsxDz4UjjBd2PUSC4KEq-VhRxguWPfheYxxmPXzCsxBG38AsmPOCdjIMNxuO1UmR2dRYPf6FuqyYqcxpynrAbPi0e49XMdbiVA5j0sTW1R8tn36t8bKpdi5xz-j0h6q_vtcgrDFhfhJm290a0QxLPx9tdpD0wH1U7Y0jeJZ7GuSkw3vdSzorypDHWA73C9AV1zKl0e1iyFN8yTykEfQIBlp8g7yuaDhb6iBwIfcP6HRflYZLAPbtvhm5g6FKn9wx0Fub8cI06xRcBQwDbTAUhtFYZax1PAw-Ied0E-DH0sBZRNtvOqdehr9mEdybyZjdNmdmN2-q_hyMZLjQYe1u1Rs2sgUSQP-Qf2NuuynYf3mwSlhSU93N7WWZwIqkb7mmf_flUMOkcaIcmshMRhdQ3g_EcKz5Vg6f330vqCqIUEAVgqkDzMMJTmL61hrvZlhj4M1Kp_4WdmJ0lQ2AIi5n-KkvwQe8xDwG2MN690ivZ3ibh9sgqFzR6XRVXuFFmVzSsZ_vfNcgqk2JZJqGNiXwj3tu1Uqvqr96bHDbiQKXln9VXdAvof-haDAq9P0oalL9w6PH8qePyLDrWC_S-rzjllyGmj7p4nMH2mk0KmGQneUejYo_RP8_B6IZ7YBYcriUYxX0Yqlui5LOcYZVHy6gVBAPaGOBPTlvU9-DHuevc4CoUl62iEnGOrTX-eaK9J9WE5LIiKWRpwfL9pbVW9faVu3G1jtxs7b3FmU9eFqJBFxI9qRguevnfoFwWiyccNhir8Ibr7XxsU_sbV_qz8AvSJKfKQlJdGYSjx64HopYURAy-bJOkub1ZL5Z_0MIv3irPvXPChWjl4AiraVW3jCfT1W7Wg2_SXJOy9xUA45A.6tLHED0cUfNByRTwoUWzaw",
    "cf_clearance": "qX_ViEpb0v_nlDVGmsguPDADH0he7x5rBAuALAJ3vwI-1670837472-0-160",
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
}

hello_chatbot = Chatbot(config, conversation_id=None)


class MainHandler(tornado.web.RequestHandler):

    def __init__(self, *argc, **argkw):
        super(MainHandler, self).__init__(*argc, **argkw)

    def options(self):
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

    def get(self):
        # get 请求
        question = self.get_argument('question')
        response = hello_chatbot.get_chat_response(str(question), output="stream")
        result = None
        for res in response:
            result = res
        result_json = json.dumps(result)
        # print(result_json)
        self.write(result_json)

    def post(self):
        # post请求
        body = self.request.body
        body_decode = body.decode()
        body_json = json.loads(body_decode)
        question = body_json.get("question")
        response = hello_chatbot.get_chat_response(str(question), output="stream")
        result = None
        for res in response:
            result = res
        result_json = json.dumps(result)
        # print(result_json)
        self.write(result_json)


application = tornado.web.Application([(r"/chat", MainHandler), ])

if __name__ == "__main__":
    application.listen(8848)
    tornado.ioloop.IOLoop.instance().start()
