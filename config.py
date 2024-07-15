import re
import os
import time

id_pattern = re.compile(r'^.\d+$')


class Config(object):
    # pyro client config
    API_ID = os.environ.get("API_ID", "21189715")  # ⚠️ Required
    API_HASH = os.environ.get("API_HASH", "988a9111105fd2f0c5e21c2c2449edfd")  # ⚠️ Required
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7355530279:AAFGSCQ86so9apCFlukmtLWjosTesCSgNn0")  # ⚠️ Required

    # database config
    DB_URL = os.environ.get("DB_URL", "mongodb+srv://ayanosuvii0925:subhichiku123@cluster0.uw8yxkl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # ⚠️ Required
    DB_NAME = os.environ.get("DB_NAME", "AutoAcceptBot")

    # other configs
    BOT_UPTIME = time.time()
    START_PIC = os.environ.get("START_PIC", "https://te.legra.ph/file/05355ddcf792cc2912566.jpg")
    ADMIN = int(os.environ.get('ADMIN', '7181106700'))  # ⚠️ Required
    DEFAULT_WELCOME_MSG = os.environ.get("WELCOME_MSG", "Hey {user},\nYour Request Approved ✅,\n\nWelcome to **{title}**")
    DEFAULT_LEAVE_MSG = os.environ.get("LEAVE_MSG", "By {user},\nSee You Again 👋\n\nFrom **{title}**")

    # user client config
    SESSION = os.environ.get("SESSION", "BQHIjPwAn1gI_vtQ0mckg34CBXq8FJPk1J67eBgtvJsyDOFT3jEvzQE877UYR2tMX_c-8QIQKUJXttzAoXZCyLnGaLQzneiAEDTa9xBtPzBB_EY6bb5dC2PCdLpju5EP1wWClJt2KMDlBLsUlHxdA5ygYWXrDZbAdGk2sxMK2qs4jQOOKPsosxaaBEDGtrygPAxeGb5IZNwzuSr55CZvMZrlp_CV-XTVciRwia792nzkuzsjHcJLHhzFfoe5pBeTS1W4Z24LcICrCEdqQoNqOX_lAot1x4SjDFJMXI4VhiwXW1hXK7SYcJRzNfBAoqJwk6q1Ef7ckfuMUOCH10hDEpi0AkswAAAAGSN1vtAA")  # ⚠️ Required @SnowStringGenBot

    # wes response configuration
    WEBHOOK = bool(os.environ.get("WEBHOOK", True))
    PORT = int(os.environ.get("PORT", "4040"))


class TxT(object):

    HELP_MSG = """
<b> ADMIN Available commands:- </b>

➜ /set_welcome - To set custom welcome message (support photo & video & animation or gif)
➜ /set_leave - To set custom leave message (support photo & video & animation or gif)
➜ /option - To toggle your welcome & leave message also auto accept (whether it'll show to user or not and will auto accept or not)
➜ /auto_approves - To toggle your auto approve channel or group
➜ /status - To see status about bot
➜ /restart - To restart the bot
➜ /broadcast - To brodcast the users (only those user who has started your bot)
➜ /acceptall - To accept all the pending join requests
➜ /declineall - To decline all the pending join requests

⚠️ <b> Support HTML & Markdown formating in welcome or leave message for more info <a href=https://core.telegram.org/api/entities#:~:text=%2C%20MadelineProto.-,Allowed%20entities,-For%20example%20the> Link </a>. </b>


<b>⦿ Developer:</b> <a href=https://t.me/II_AYANO_II>Ayano ❄️</a>
"""
