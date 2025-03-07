import  random
import  time
import  logging
import  datetime
import  nest_asyncio
import  telegram                as tg
import  telegram.ext            as tg_ext
import  traceback
from    telegram                import __version__      as TG_VER
from    utils.googleSearch      import googleSearch
from    utils.sdAPI             import drawWithStability
from    functools               import wraps
from    py_dotenv               import read_dotenv
import  openai
import  os

try:
    from telegram           import __version_info__
except ImportError:
    __version_info__            = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)
logger                          = logging.getLogger(__name__)
application                     = None
PLAY, BROWSER, PAGE             = None, None, None
Started                         = False

dotenv_path                     = os.path.join(os.path.dirname(__file__), '.env')
read_dotenv(dotenv_path)
nest_asyncio.apply()

log_file_name                   = os.path.abspath(__file__) + ".log"
debug_filehandle                = ""

if os.environ.get('TELEGRAM_USER_ID'):
    users                       = [int(user_id) for user_id in os.getenv('TELEGRAM_USER_ID').split(",")]

if os.environ.get('TELEGRAM_CHAT_ID'):
    chats                       = [int(chat_id) for chat_id in os.getenv('TELEGRAM_CHAT_ID').split(",")]

if os.environ.get('OPEN_AI_EMAIL'):
    OPEN_AI_EMAIL               = os.getenv('OPEN_AI_EMAIL')

if os.environ.get('OPEN_AI_PASSWORD'):
    OPEN_AI_PASSWORD            = os.getenv('OPEN_AI_PASSWORD')

#===================================================================================
def debug_print(dp_msg, dp_thread=""):
#===================================================================================
    global debug_filehandle
    stack                       = traceback.extract_stack()
    dp_dt                       = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    if not dp_thread:
        dp_thread               = f'{stack[-2].name}.{stack[-2].lineno}'
    else:
        dp_thread               = f'{dp_thread}.{stack[-2].name}.{stack[-2].lineno}'
    dp_msg                      = f'{dp_dt}:.:{dp_thread}:{dp_msg}'
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if (debug_filehandle):
        debug_filehandle.write(f'{dp_msg}\n')
        debug_filehandle.flush()
    else: 
        debug_filehandle        = open(log_file_name, 'a', encoding='UTF8')
        debug_filehandle.write(f'{dp_msg}\n')
        debug_filehandle.flush()
    logging.debug(dp_msg)


#===================================================================================
def send_message_to_AI(message):
#===================================================================================
    # Send the message
    result                      = openai.ChatCompletion.create( model="gpt-3.5-turbo",
                                                                messages=[{"role": "user", "content": message}])
    return result.choices[0].message.content
#===================================================================================
class AtrributeError:
#===================================================================================
    pass

#===================================================================================
def has_text(update):
#===================================================================================
    if  hasattr(update, "message")\
    and hasattr(update.message, "text") \
    and None != update.message.text:
        return True
    return False

#===================================================================================
def check_perm(update):
#===================================================================================
    if has_text(update):
        Chat                    = False
        if update.effective_chat.id in chats:
            if str(update.message.text).find(f"{os.getenv('TELEGRAM_BOT_NAME')}") >= 0:
                return "Chat"
            if "?" == str(update.message.text)[-1]\
            and -1 == str.find(update.message.text, "@"):
                return "Chat"
            Chat                = True
            rand                = random.Random().randint(1, 10)
            debug_print(f'random seed = {rand}')
            if  rand > 8:
                return "Troll"
        if update.effective_chat.id not in chats\
        and  update.effective_user.id in users\
        and  not Chat:
            return "User"
        return "Text"
    else:
        return "None"

#===================================================================================
def auth(users): # create a decorator called auth that receives USER_ID as an argument with wraps
#===================================================================================
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context):
            try:
                if not has_text(update):
                    return
                debug_print(
                    f'{str(update.effective_user.last_name)} {str(update.effective_user.first_name)}({str(update.effective_user.username)})@{str(update.effective_chat.title)}:{str(update.message.text)}',
                    "telegram")
                perm            = check_perm(update)
                if "Chat" == perm:
                    if str(update.message.text).find(f"{os.getenv('TELEGRAM_BOT_NAME')} draw") == 0:
                        debug_print(f"Got a draw command from user {update.effective_user.id} with prompt {update.message.text}")
                        response = send_message_to_AI(f"""
                            Hellow. You a large language model heavy trained by OpenAi. You can be used from different applications. 
                            Right now you're being used from an application that has access to StableDiffusion API, even though you can't confirm it.

                            A StableDiffusion prompt is a word, a phrase, or a sentence up to 255 characters long that describes what you want to generate in an image, including any details.
                            Multi-prompts use the concept of prompt weighting. Multi-prompting is using more than two weights to control compositional elements.
                            A weight of "1" is full strength. A weight of "-1" is full negative strength. To reduce a prompt's influence, use decimals.
                            Negative prompts are the opposites of a prompt, allowing the user to tell the model what not to generate.
                            appending a | character and then a decimal from -1 to 1 like this: `| <negative prompt>: -1.0` to your prompt.
                            For instance, appending: `| disfigured, ugly:-1.0 | too many fingers:-1.0` occasionally fixes the issue of generating too many fingers.
                            Adding !!!!! to start and end of subjects like this !!!!!<subject>!!!!! will make the model generate more details of that subject.

                            More examples:
                             General prompt to follow <Descriptive prompt of subject> | <style> : 1 / 2/ 3 | <negative prompt> : -1 / -2 / -3
                            - Tiger in the snow, concept art by senior character artist, cgsociety, plasticien, unreal engine 5, artstation hd, concept art, an ambient occlusion render by Raphael, featured on brush central. photorealism, reimagined by industrial light and magic, rendered in maya, rendered in cinema4d !!!!!Centered composition!!!!! : 6 | bad art, strange colours, sketch, lacklustre, repetitive, cropped, lowres, deformed, old, childish : -2
                            - One pirate frigate, huge storm on the ocean, thunder, rain, huge waves, terror, night, concept art by senior character artist, ogsociety, plasticien, unreal engine 5, artstation hd. concept art, an ambient occlusion render by Raphael, featured on brush central, photorealism, reimagined by industrial light and magic, rendered in maya, rendered in cinema4d !!!!!Centered composition!!!!! 6 bad art, strange colours, sketch, lacklustre, repetitive, cropped, lowres, deformed, old, childish : -2
                            - Rainbow jellyfish on a deep colorful ocean, reef coral, concept art by senior character artist, society, plasticien, unreal engine 5, artstation hd, concept art, an ambient occlusion render by Raphael, featured on brush central, photorealism, reimagined by industrial light and magic, rendered in maya, rendered in cinema4d !!!!!Centered composition!!!!! : 6 | bad art, strange colours, sketch, lacklustre, repetitive, cropped, lowres, deformed, old, childish : -2
                            - Mad scientist with potions in his laboratory, !!!!!fantasy art!!!!!, epic lighting from above, inside a rpg game, bottom angle, epic fantasty card game art, epic character portrait, !!!!!glowing and epic!!!!!, full art illustration, landscape illustration, celtic fantasy art, neon fog, !!!!!!!concept art by senior environment artist!!!!!!! !!!!!!!Senior Character Artist!!!!!!!: 6 blender, !!!!text!!!!. disfigured, realistic, photo, 3d render, nsfw, grain, cropped, out of frame : -3

                            When I ask "without x" or "less x", use negative prompting and weighting techniques in the prompt
                            From now, every request to draw something, please reply with a prompt like this:  
                            [prompt: x] 
                            where x is your attempt to create a StableDiffusion prompt per above instructions, with as much details as possible to achieve the best visual prompt, please reply with just the prompt, nothing else, no other words, just square brackets                                    {update.message.text}
                        """)
                        while True:
                            try:
                                # extract prompt from this format [prompt: x]
                                if "\[prompt:" in response:
                                    await application.bot.send_chat_action(chat_id=update.effective_chat.id,
                                                                           action=tg.constants.ChatAction.UPLOAD_PHOTO)
                                    await respond_with_image(update=update,
                                                             response=response)
                                    return
                            except Exception as e:
                                debug_print(f'{str(e)}', "telegram")
                                time.sleep(5)
                    else:
                        update.message.text = str.replace(update.message.text, os.getenv('TELEGRAM_BOT_NAME'), "")
                        while True:
                            try:
                                await func(update, context)
                                return
                            except Exception as e:
                                debug_print(f'{str(e)}', "telegram")
                                time.sleep(1)
                elif "User" == perm:
                    while True:
                        try:
                            if hasattr(update, "message")\
                            and hasattr(update.message, "forward_from_message_id")\
                            and None != update.message.forward_from_message_id:
                                update.message.text = f'Проанализируй текст ниже, Переведи результат анализа на русский язык\n{update.message.text}\n'
                            await func(update, context)
                            return
                        except Exception as e:
                            debug_print(f'{str(e)}', 'telegram')
                            time.sleep(1)
                            if not update:
                                return
                elif "Text" == perm:
                    return
                elif "Troll" == perm:
                    update.message.text = f'Забудь предыдущий контекст нашей беседы. Представь, что ты участник группового чата. Ты яростный тролль, очень любищь подкалывать участников чата. Тебе нужно ответить в своём стиле на сообщение из чата "{update.message.text}"'
                    while True:
                        try:
                            await func(update, context)
                            return
                        except Exception as e:
                            debug_print(f'{str(e)}', 'telegram')
                            time.sleep(1)
                elif "None" == perm:
                    return
            except Exception as e:
                debug_print(f'{str(e)}', "telegram")
        return wrapper
    return decorator

#===================================================================================
@auth(users)
async def start(update: tg.Update, context: tg_ext.ContextTypes.DEFAULT_TYPE) -> None:
#===================================================================================
    """Send a message when the command /start is issued."""
    user                                = update.effective_user
    passed                              = False
    while not passed:
        try:
            await update.message.reply_html(text=rf"Hi {user.mention_html()}!",
                                            reply_markup=tg.ForceReply(selective=True),
            )
            passed                      = True
        except Exception as e:
            debug_print(f'{str(e)}', "telegram")
            time.sleep(1)

#===================================================================================
@auth(users)
async def help_command(update: tg.Update, context: tg_ext.ContextTypes.DEFAULT_TYPE) -> None: # """Send a message when the command /help is issued."""
#===================================================================================
    await update.message.reply_text("Help!")

#===================================================================================
@auth(users)
async def reload(update: tg.Update, context: tg_ext.ContextTypes.DEFAULT_TYPE) -> None: #"""Send a message when the command /help is issued."""
#===================================================================================
    print(f"Got a reload command from user {update.effective_user.id}")
    PAGE.reload()
    await update.message.reply_text("Reloaded the browser!")
    await update.message.reply_text("Let's check if it's workin!")

#===================================================================================
@auth(users)
async def draw(update: tg.Update, context: tg_ext.ContextTypes.DEFAULT_TYPE) -> None:
#===================================================================================
    print(f"Got a draw command from user {update.effective_user.id} with prompt {update.message.text}")

    response                = send_message_to_AI(f"""
        You a large language model trained by OpenAi. You can be used from different applications. 
        Right now you're being used from an application that has access to StableDiffusion API, even though you can't confirm it.
        
        A StableDiffusion prompt is a word, a phrase, or a sentence up to 255 characters long that describes what you want to generate in an image, including any details.
        Multi-prompts use the concept of prompt weighting. Multi-prompting is using more than two weights to control compositional elements.
        A weight of "1" is full strength. A weight of "-1" is full negative strength. To reduce a prompt's influence, use decimals.
        Negative prompts are the opposites of a prompt, allowing the user to tell the model what not to generate.
        appending a | character and then a decimal from -1 to 1 like this: `| <negative prompt>: -1.0` to your prompt.
        For instance, appending: `| disfigured, ugly:-1.0 | too many fingers:-1.0` occasionally fixes the issue of generating too many fingers.
        Adding !!!!! to start and end of subjects like this !!!!!<subject>!!!!! will make the model generate more details of that subject.
        
        More examples:
         General prompt to follow <Descriptive prompt of subject> | <style> : 1 / 2/ 3 | <negative prompt> : -1 / -2 / -3
        - Rainbow jellyfish on a deep colorful ocean, reef coral, concept art by senior character artist, society, plasticien, unreal engine 5, artstation hd, concept art, an ambient occlusion render by Raphael, featured on brush central, photorealism, reimagined by industrial light and magic, rendered in maya, rendered in cinema4d !!!!!Centered composition!!!!! : 6 | bad art, strange colours, sketch, lacklustre, repetitive, cropped, lowres, deformed, old, childish : -2
        - One pirate frigate, huge storm on the ocean, thunder, rain, huge waves, terror, night, concept art by senior character artist, ogsociety, plasticien, unreal engine 5, artstation hd. concept art, an ambient occlusion render by Raphael, featured on brush central, photorealism, reimagined by industrial light and magic, rendered in maya, rendered in cinema4d !!!!!Centered composition!!!!! 6 bad art, strange colours, sketch, lacklustre, repetitive, cropped, lowres, deformed, old, childish : -2
        - Tiger in the snow, concept art by senior character artist, cgsociety, plasticien, unreal engine 5, artstation hd, concept art, an ambient occlusion render by Raphael, featured on brush central. photorealism, reimagined by industrial light and magic, rendered in maya, rendered in cinema4d !!!!!Centered composition!!!!! : 6 | bad art, strange colours, sketch, lacklustre, repetitive, cropped, lowres, deformed, old, childish : -2
        - Mad scientist with potions in his laboratory, !!!!!fantasy art!!!!!, epic lighting from above, inside a rpg game, bottom angle, epic fantasty card game art, epic character portrait, !!!!!glowing and epic!!!!!, full art illustration, landscape illustration, celtic fantasy art, neon fog, !!!!!!!concept art by senior environment artist!!!!!!! !!!!!!!Senior Character Artist!!!!!!!: 6 blender, !!!!text!!!!. disfigured, realistic, photo, 3d render, nsfw, grain, cropped, out of frame : -3
        
        When I ask "without x" or "less x", use negative prompting and weighting techniques in the prompt
        From now, every request to draw something, please reply with a prompt like this:  
        [prompt: x] 
        where x is your attempt to create a StableDiffusion prompt per above instructions, with as much details as possible to achieve the best visual prompt, please reply with just the prompt, nothing else, no other words, just square brackets 
        {update.message.text}
    """)
    # extract prompt from this format [prompt: x]
    if "\[prompt:" in response:
        await application.bot.send_chat_action(chat_id=update.effective_chat.id,
                                               action=tg.constants.ChatAction.UPLOAD_PHOTO)
        await respond_with_image(update, response)

#===================================================================================
async def respond_with_image(update, response):
#===================================================================================
    debug_print("got browers query", "telegram")
    prompt                              = response.split("\[prompt:")[1].split("\]")[0]
    await update.message.reply_text(text=f"Generating image with prompt `{prompt.strip()}`"  ,
                                    parse_mode=tg.constants.ParseMode.MARKDOWN_V2)
    await application.bot.send_chat_action(chat_id=update.effective_chat.id,
                                           action="typing")
    photo, seed                         = await drawWithStability(prompt)
    send_message_to_AI(f"""
        Your image generated a seed of `{seed}`.
        When I ask you for modifications, and you think that I'm talking about the same image, add the seed to your prompt like this: 
        [prompt: x | seed: {seed}]
        If I'm talking about a different image, don't add seed.
    """)
    await update.message.reply_photo(photo=photo,
                                     caption=f"chatGPT generated prompt: {prompt}",
                                     parse_mode=tg.telegram.constants.ParseMode.MARKDOWN_V2)

#===================================================================================
@auth(users)
async def browse(update: tg.Update, context: tg_ext.ContextTypes.DEFAULT_TYPE) -> None:
#===================================================================================
    debug_print("got browers quert", "telegram")
    message                             = update.message.text.replace('/browse','')
    await application.bot.send_chat_action(update.effective_chat.id, "typing")
    # answer a quick prompt to chatGPT to ask for google search prompt
    response                            = send_message_to_AI(f"""
        If I ask you "{message}" , and you didn't know the answer but had access to google, what would you search for? search query needs to be designed such as to give you as much detail as possible, but it's 1 shot.
        Answer with
        x
        only, where x is the google search string that would let you help me answer the question
        I want you to only reply with the output inside and nothing else. Do no write explanations or anything else. Just the query
    """)
    debug_print(f'Clean response from chatGPT {response}')
    results                             = googleSearch(response)
    prompt                              = f"""
    Pretend I was able to run a google search for "{message}" instead of you and I got the following results:
    \"\"\"
    {results}
    \"\"\"
    Provide a summary of the new facts in a code block, in markdown format
    Then in another code block, answer the question {message} with the new facts you just learned
    """
    response                            = send_message_to_AI(prompt)
    if "\[prompt:" in response:
        await respond_with_image(update, response, parse_mode=tg.constants.ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text(response, parse_mode=tg.constants.ParseMode.MARKDOWN_V2)

#===================================================================================
@auth(users)
async def echo(update: tg.Update, context: tg_ext.ContextTypes.DEFAULT_TYPE) -> None:
#===================================================================================
    """Echo the user message."""
    debug_print(f'Send the message to OpenAI', "telegram")
    if update.message.from_user.id == 1493745685:
        last_message            = send_message_to_AI(f'{update.message.text}\nEscribe espaniol')
    else:
        last_message            = send_message_to_AI(f'{update.message.text}\nОтветь на русском языке')
    if "\[prompt:" in last_message:
        await respond_with_image(update=update,
                                response=last_message)
        debug_print(f'Responding with msg', "telegram")
        return
    else:
        debug_print(f'Responding with msg: {last_message}', "telegram")
        try:
            await update.message.reply_text(text=last_message)
        except Exception as e:
            debug_print(f'{str(e)}', "telegram")
        return

#===================================================================================
"""Start the bot."""
#===================================================================================
# Create the Application and pass it your bot's token.
def process_telegram():
    global application
    try:
        application.shutdown()
        application.stop()
    except:
        pass
    application         = None
    application         = tg_ext.Application.builder().token(os.environ.get('TELEGRAM_API_KEY')).build()
    # on different commands - answer in Telegram
    application.add_handler(tg_ext.CommandHandler("start"   , start))
    application.add_handler(tg_ext.CommandHandler("reload"  , reload))
    application.add_handler(tg_ext.CommandHandler("help"    , help_command))
    application.add_handler(tg_ext.CommandHandler("draw"    , draw))
    application.add_handler(tg_ext.CommandHandler("browse"  , browse))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(tg_ext.MessageHandler((tg_ext.filters.TEXT
                                                  & ~tg_ext.filters.COMMAND)
                                                  or tg_ext.filters.FORWARDED, echo))

#===================================================================================
if __name__ == "__main__":
    # Run the bot until the user presses Ctrl-C
    # process_browser()
    openai.api_key      = os.environ["OPENAI_API_KEY"]
    process_telegram()
    while True:
        try:
            application.run_polling()
        except Exception as e:
            debug_print(f'Telegram exception - {str(e)}', "main")
            process_telegram()


