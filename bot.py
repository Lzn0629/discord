import os
import discord 
import random
import sqlite3
from discord.ext import commands
from datetime import datetime

token = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="", intents=intents) #發送訊息前的字元

@bot.command(name="gay") #一般訊息回覆
async def gay(ctx):
    await ctx.send("你才是gay")
@bot.command(name="誰是最呆的") #一般訊息回覆
async def cute(ctx):
    await ctx.send("埋埋是最呆的")
@bot.command(name="對吧我也是這樣想") #一般訊息回覆
async def too(ctx):
    await ctx.send("對阿 超級呆")
@bot.command(name="QAQ") #一般訊息回覆
async def QAQ(ctx):
    await ctx.send("QAQ")

@bot.command(name="現在幾點")
async def time(ctx):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    await ctx.send(f"現在時刻: {current_time}") 

@bot.hybrid_command(name="add") #註冊成官方的 /觸發的命令 ->但是需要經過同步服務器
async def add(ctx, a: int, b: int):
    await ctx.send(a+b)

#同步服務器
@bot.command(name="Re")#沒寫成hybrid 是因為希望向用戶隱藏
@commands.has_permissions(administrator=True) #強制管理員才可使用
async def Re(ctx):
    await bot.tree.sync() #同步服務器
    await ctx.send("同步完成") 

#剪刀石頭布
@bot.hybrid_command(nmae="play") 
async def play(ctx):
    await ctx.send("運氣 也是實力的一部分喔", view= PlayView())

class PlayView(discord.ui.View):
    def get_contect(self, label):
        choices = ["剪刀", "石頭", "布"] #選擇有這些
        opponent_choice = random.choice(choices)  # 隨機選擇對手的出拳
        result = self.get_result(label, opponent_choice)
        return f"你出了{label}, 對手出了{opponent_choice}, {result}" #來判斷玩家與對手的出拳結果，並將結果存儲在 result

    def get_result(self, player, opponent):
        if player == opponent:
            return "平手了"
        elif (player == "剪刀" and opponent == "布") or \
             (player == "石頭" and opponent == "剪刀") or \
             (player == "布" and opponent == "石頭"):
            return "你贏了"
        else:
            return "你輸了"
            
    @discord.ui.button(label="剪刀", style=discord.ButtonStyle.green, emoji="✂️") #按鍵設定
    async def scissors(self, interaction: discord.Integration, button: discord.ui.Button): #需要拿到兩筆資料
        await interaction.response.edit_message(content=self.get_contect(button.label))

    @discord.ui.button(label="石頭", style=discord.ButtonStyle.green, )
    async def rock(self, interaction: discord.Integration, button: discord.ui.Button):
        await interaction.response.edit_message(content=self.get_contect(button.label))

    @discord.ui.button(label="布", style=discord.ButtonStyle.green, )
    async def paper(self, interaction: discord.Integration, button: discord.ui.Button):
        await interaction.response.edit_message(content=self.get_contect(button.label))

    @discord.ui.button(label="不想玩了", style=discord.ButtonStyle.red)
    async def STOP(self, interaction: discord.Integration, button: discord.ui.Button):
        await interaction.response.edit_message(content="回家多練練吧", view=None)   

#學校功能
@bot.hybrid_command(name="行事曆")
async def lir(ctx):
    if os.path.exists("day1.png"):
        await ctx.send(file=discord.File("day1.png"))
        await ctx.send(file=discord.File("day2.png"))
    else:
        await ctx.send("抱歉，找不到行事曆")

#我的救星
default_lunch_options = ["麥當勞", "烏龍麵", "自助餐", "超商", "早餐店"]

@bot.hybrid_command(name="午餐要吃什麼")
async def lunch_options(ctx):
    view = LunchOptionsView()
    await ctx.send("您的午餐選擇方式：", view=view)

class LunchOptionsView(discord.ui.View):
    @discord.ui.button(label="自行輸入選項並隨機選擇", style=discord.ButtonStyle.green)
    async def custom_input(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("請輸入您的午餐選項，用逗號分隔（例如：烏龍麵, 漢堡, 壽司）：")

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        msg = await bot.wait_for('message', check=check)  # 等待並取得用戶的輸入
        user_input = msg.content.split(",")
        choice = random.choice(user_input)
        await interaction.followup.send(f"隨機選擇的午餐是：{choice}")


    @discord.ui.button(label="使用系統內建選項", style=discord.ButtonStyle.red)
    async def system_default(self, interaction: discord.Integration, button: discord.ui.Button):
        choice = random.choice(default_lunch_options)
        await interaction.response.send_message(f"隨機選擇的午餐是：{choice}")

#課表系統
if not os.path.exists('schedules'):
    os.makedirs('schedules')

@bot.hybrid_command(name="上傳課表")
async def upload_schedule(ctx):
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        file_path = f"schedules/{ctx.author.id}.png"
        
        try:
            # 保存圖片到指定路徑
            await attachment.save(file_path)
            # 將文件路徑和用戶 ID 存儲到數據庫中
            conn = sqlite3.connect('schedules.db')
            c = conn.cursor()
            c.execute("REPLACE INTO schedules (user_id, file_path) VALUES (?, ?)", (str(ctx.author.id), file_path))
            conn.commit()
            conn.close()

            await ctx.send("課表已上傳成功！")
        except Exception as e:
            await ctx.send(f"上傳課表時發生錯誤：{str(e)}")
    else:
        await ctx.send("請上傳課表圖片。")

@bot.hybrid_command(name="課表")
async def send_schedule(ctx):
    try:
        conn = sqlite3.connect('schedules.db')
        c = conn.cursor()

        # 從數據庫中檢索文件路徑
        c.execute("SELECT file_path FROM schedules WHERE user_id = ?", (str(ctx.author.id),))
        result = c.fetchone()
        conn.close()

        if result:
            file_path = result[0]
            if os.path.exists(file_path):
                await ctx.send(file=discord.File(file_path))
            else:
                await ctx.send("抱歉，找不到你的課表圖片。")
        else:
            await ctx.send("你還沒有上傳過課表圖片 請先使用上傳課表的命令來上傳你的課表。")
    except Exception as e:
        await ctx.send(f"獲取課表時發生錯誤：{str(e)}")

# 確保事件處理器被啟用
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith(('.png', '.jpg', '.jpeg')):
                file_path = f"schedules/{message.author.id}.png"
                await attachment.save(file_path)
                conn = sqlite3.connect('schedules.db')
                c = conn.cursor()
                c.execute("REPLACE INTO schedules (user_id, file_path) VALUES (?, ?)", (str(message.author.id), file_path))
                conn.commit()
                conn.close()
                await message.channel.send("課表圖片已保存。")
    
    await bot.process_commands(message)

bot.run(token)
