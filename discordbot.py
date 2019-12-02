import discord
from discord.ext import commands
import asyncio
import sys
import os
import traceback

bot = commands.Bot(command_prefix='.')
token = os.environ['DISCORD_BOT_TOKEN']

@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')
    
@bot.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@bot.command()
async def 募集(ctx, about = "募集", cnt = 5, settime = 86400.0):
    cnt, settime = int(cnt), float(settime)
    reaction_member = ["♦参加者一覧♦"]
    reaction_emoji = "✋参加/☠参加取消/⛔募集停止"
    test = discord.Embed(title=f"現在の {about} 募集状況",colour=0x1e90ff)
    test.add_field(name=f"あと{cnt}人 募集中\n", value=None, inline=True)
    msg = await ctx.send(embed=test)
    msg2 = await ctx.send(reaction_emoji)
    
    #投票の欄
    await msg.add_reaction('✋')
    await msg.add_reaction('☠')
    await msg.add_reaction('⛔')

    def check(reaction, user):
        emoji = str(reaction.emoji)
        if user.bot == True:    # botは無視
            pass
        else:
            return emoji == '✋' or emoji == '☠' or emoji == '⛔'

    while len(reaction_member)-1 <= cnt:
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=settime, check=check)
        except asyncio.TimeoutError:
            await msg.delete()#メッセージの削除
            await msg2.delete()#メッセージの削除
            await ctx.send('残念、人が足りなかったようだ...')
            break
        else:
            print(str(reaction.emoji))
            if str(reaction.emoji) == '✋':
                reaction_member.append(user.name)
                cnt -= 1
                test = discord.Embed(title=f"現在の　{about} 募集状況",colour=0x1e90ff)
                test.add_field(name=f"あと__{cnt}__人 募集中\n", value='\n'.join(reaction_member), inline=True)
                await msg.edit(embed=test)

                if cnt == 0:
                    test = discord.Embed(title=f"現在 {about} 募集状況",colour=0x1e90ff)
                    test.add_field(name=f"あと__{cnt}__人 募集中\n", value='\n@'.join(reaction_member), inline=True)
                    await msg.edit(embed=test)
                    finish = discord.Embed(title=f"{about} 募集終了（満員御礼）",colour=0xFF0000)
                    finish.add_field(name="仲間が集まったようだ。",value='\n@'.join(reaction_member), inline=True)
                    msg3 = await ctx.send(embed=finish)                                 
                    await msg.delete()#メッセージの削除
                    await msg2.delete()#メッセージの削除
                    #await asyncio.sleep(10)
                    #await msg3.delete()#メッセージの削除

            elif str(reaction.emoji) == '☠':
                if user.name in reaction_member:
                    reaction_member.remove(user.name)
                    cnt += 1
                    test = discord.Embed(title=f"現在の　{about} 募集状況",colour=0x1e90ff)
                    test.add_field(name=f"あと__{cnt}__人 募集中\n@", value='\n'.join(reaction_member), inline=True)
                    await msg.edit(embed=test)
                else:
                    pass
        # リアクション消す。メッセージ管理権限がないとForbidden:エラーが出ます。
        await msg.remove_reaction(str(reaction.emoji), user)
        
@bot.command()
async def アンケート(ctx, about = "question", *args):
    emojis = ["1⃣","2⃣","3⃣","4⃣"]

    cnt = len(args)
    message = discord.Embed(title=":speech_balloon: "+about,colour=0x1e90ff)
    if cnt <= len(emojis):
        for a in range(cnt):
            message.add_field(name=f'{emojis[a]}{args[a]}', value="** **", inline=False)
        msg = await ctx.send(embed=message)
        #投票の欄
        for i in range(cnt):
            await msg.add_reaction(emojis[i])
    else:
        await ctx.send("悪い...項目は4つまでなんだ...")


bot.run(token)
