import os
from dotenv import load_dotenv

import discord
from discord.ext import commands
import asyncio
import random

load_dotenv()

# ボットの設定
BOT_TOKEN = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.reactions = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()  # スラッシュコマンドをサーバーに同期
    print(f"ログインしました: {bot.user}")

@bot.tree.command(name="randomrole", description="リアクションで役割をランダムに割り振ります。")
async def randomrole(interaction: discord.Interaction):
    countdown = 15  # カウントダウン秒数
    max_players = 5  # 最大参加人数
    reaction_emoji = "👍"

    message = await interaction.response.send_message(f"試合に参加する方はリアクションを押してください（残り{countdown}秒）", ephemeral=False)
    msg = await interaction.original_response()
    await msg.add_reaction(reaction_emoji)

    # カウントダウン処理
    for i in range(countdown, 0, -1):
        await asyncio.sleep(1)
        await msg.edit(content=f"試合に参加する方はリアクションを押してください（残り{i}秒）")

        updated_msg = await interaction.channel.fetch_message(msg.id)
        reaction = discord.utils.get(updated_msg.reactions, emoji=reaction_emoji)
        users = [user async for user in reaction.users() if not user.bot]

        if (len(users) == 5):
            break

    await msg.edit(content="試合に参加する方はリアクションを押してください（投票終了）")

    updated_msg = await interaction.channel.fetch_message(msg.id)
    reaction = discord.utils.get(updated_msg.reactions, emoji=reaction_emoji)
    users = [user async for user in reaction.users() if not user.bot]

    if len(users) == 0:
        await interaction.followup.send("誰も参加しませんでした。")
        return

    roles = ["デュエリスト", "イニシエーター", "センチネル", "コントローラー"]
    assigned_roles = {}

    # 役割をシャッフルし、4人に異なる役割を振り分け
    shuffled_roles = roles.copy()
    random.shuffle(shuffled_roles)

    for i, user in enumerate(users[:4]):
        assigned_roles[user] = shuffled_roles[i]

    # 5人目のプレイヤーにはランダムな役割を1つ割り当て
    if len(users) == 5:
        assigned_roles[users[4]] = random.choice(roles)

    # 結果を送信
    result_message = "今回の役割はこちらに決定しました。\n"
    for user, role in assigned_roles.items():
        result_message += f"{user.mention}: {role}\n"

    await interaction.followup.send(f"{result_message}")

bot.run(BOT_TOKEN)
