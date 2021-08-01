import discord,json,random
from discord.ext import commands
from main import client

from cogs.economy_manager import *


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready():
        print("Economy is loaded")

    @commands.command()
    async def balance(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        await open_account(member)
        user = member
        users = await get_bank_data()

        wallet_amt = users[str(user.id)]["wallet"]
        bank_amt = users[str(user.id)]["bank"]

        eme = discord.Embed(title=f"{user.name}'s balance", color=ctx.author.color)
        eme.add_field(name="Wallet", value=wallet_amt, inline=False)
        eme.add_field(name="Bank", value=bank_amt, inline=False)
        eme.add_field(name="Net Worth", value=f"{bank_amt + wallet_amt}", inline=False)
        await ctx.send(embed=eme)

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def beg(self, ctx):
        await open_account(ctx.author)

        users = await get_bank_data()
        user = ctx.author
        earnings = random.randrange(501)

        em=discord.Embed(title="Beg", description=f"Someone Gave you {earnings} coins!", color=discord.Color.green())
        await ctx.send(embed=em)

        users[str(user.id)]["wallet"] += earnings

        with open("storage_data/bank.json", "w") as f:
            json.dump(users, f, indent=4)

    @commands.command()
    @commands.cooldown(1, 84000, commands.BucketType.user)
    async def daily(self, ctx):
        await open_account(ctx.author)

        users = await get_bank_data()
        user = ctx.author
        earnings = random.randrange(1000, 10000)

        em=discord.Embed(title="Daily", description=f"Heres your daily Salary: {earnings}")
        await ctx.send(embed=em)

        users[str(user.id)]["wallet"] += earnings

        with open("storage_data/bank.json", "w") as f:
            json.dump(users, f, indent=4)

    @commands.command()
    @commands.cooldown(1, 12000, commands.BucketType.user)
    async def work(self, ctx):
        await open_account(ctx.author)

        users = await get_bank_data()
        user = ctx.author
        earnings = random.randrange(1000, 5000)

        em=discord.Embed(title="Work", description=f"Keep working hard! Heres your salary: {earnings}")
        await ctx.send(embed=em)

        users[str(user.id)]["wallet"] += earnings

        with open("storage_data/bank.json", "w") as f:
            json.dump(users, f, indent=4)

    @commands.command(aliases=["lb", "rich"])
    async def leaderboard(self, ctx, x=1):
        users = await get_bank_data()
        leader_board = {}
        total = []
        for user in users:
            name = int(user)
            total_amount = users[user]["wallet"] + users[user]["bank"]
            leader_board[total_amount] = name
            total.append(total_amount)

        total = sorted(total, reverse=True)

        em = discord.Embed(
            title=f"Top {x} Richest People",
            description="This is decided on the basis of raw money in the bank and wallet",
            color=ctx.author.color,
        )
        index = 1
        for amt in total:
            id_ = leader_board[amt]
            member = client.get_user(id_)
            name = member.name
            em.add_field(name=f"{index}. {name}", value=f"{amt}", inline=False)
            if index == x:
                break
            else:
                index += 1

        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shop(self, ctx):
        em = discord.Embed(title="__Shop__ :shopping_cart:",
                        color=discord.Color.green())

        for item in mainshop:
            name = item["name"]
            price = item["price"]
            desc = item["description"]
            em.add_field(name=name,
                        value=f":coin:{price} | {desc}")

        await ctx.send(embed=em)


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def buy(self, ctx, item, amount=1):
        await open_account(ctx.author)

        res = await buy_this(ctx.author, item, amount)

        if not res[0]:
            if res[1] == 1:
                await ctx.send("That Object isn't there!")
                return
            if res[1] == 2:
                await ctx.send(
                    f"You don't have enough money in your wallet to buy :coin:{amount} {item}!"
                )
                return

        await ctx.send(f"You just bought {amount} {item}!")




    @commands.command(aliases=["inv"])
    async def inventory(self, ctx):
        await open_account(ctx.author)
        user = ctx.author
        users = await get_bank_data()

        try:
            inventory = users[str(user.id)]["bag"]

        except KeyError:
            return await ctx.send(f"error_msg")
            
            
        em_inv = discord.Embed(title="__Inventory__", color = discord.Color.green())
        for item in inventory:
            name = item["item"]
            amount = item["amount"]

            if not amount == 0:
                em_inv.add_field(name=name, value=amount, inline=False)

            

            await ctx.send(embed=em_inv)

    @commands.command(aliases=["with"])
    async def withdraw(self, ctx, amount=None):
        await open_account(ctx.author)
        if amount == None:
            await ctx.send("Ok, you wanna tell me how much you want to withdraw now?")
            return

        bal = await update_bank(ctx.author)
        amount = int(amount)
        if amount == "all":
            amount = bal[0]

        if amount > bal[1]:
            await ctx.send("You don't have that much money")
            return

        if amount < 0:
            await ctx.send("amount must be postitive")
            return

        await update_bank(ctx.author, amount)
        await update_bank(ctx.author, -1 * amount, "bank")

        await ctx.send(f"You withdrew {amount} of coins!")

    @commands.command(aliases=['Sell, SELL'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def sell(self, ctx, item, amount=1):
        await open_account(ctx.author)

        res = await sell_this(ctx.author, item, amount)

        if not res[0]:
            if res[1] == 1:
                await ctx.send("That Object isn't there!")
                return
            if res[1] == 2:
                await ctx.send(f"You don't have {amount} {item} in your inventory.")
                return
            if res[1] == 3:
                await ctx.send(f"You don't have {item} in your inventory.")
                return

        await ctx.send(
            f"You just sold {amount} {item}.")

    @commands.command(aliases=["r"])
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def rob(self, ctx, member: discord.Member):
        await open_account(ctx.author)
        await open_account(member)

        bal = await update_bank(member)

        if bal[0] < 1000:
            embed = discord.Embed(
                title="Not Worth It",
                discription="Not worht it man, its not worth robbing him",
                color=ctx.author.color,
            )

        earnings = random.randrange(0, bal[0])

        await update_bank(ctx.author, earnings)
        await update_bank(member, -1 * earnings)

        embed = discord.Embed(
            title="Congratulations!",
            description=f"Congratulations! you robbed {earnings} coins",
            color=ctx.author.color,
        )

        await ctx.send(embed=embed)

    @commands.command(aliases=["dep"])
    async def deposit(self, ctx, amount=None):
        try:
            await open_account(ctx.author)
            if amount == None:
                await ctx.send(
                    "Ok, you wanna tell me how much you want to deposit now?"
                )
                return

            bal = await update_bank(ctx.author)
            amount = int(amount)
            if amount == "all":
                amount = "wallet"
                await update_bank(ctx.author, -1 * amount)
                await update_bank(ctx.author, amount, "bank")
                return
            if amount > bal[0]:
                await ctx.send("You don't have that much money")
                return

            if amount < 0:
                await ctx.send("amount must be postitive")
                return

            await update_bank(ctx.author, -1 * amount)
            await update_bank(ctx.author, amount, "bank")

            await ctx.send(f"You deposited {amount} of coins!")
        except ValueError:
            await ctx.send("You didn't enter a number")

    @commands.command(aliases=['am'])
    @commands.has_permissions(administrator=True)
    async def addmoney(self, ctx, amount=None, user: discord.Member = None):
        if user == None:
            user = ctx.author
        elif amount == None:
            await ctx.send("Enter the amount of money to be added")
            return
        await open_account(user)
        amount = int(amount)
        users = await get_bank_data()
        users[str(user.id)]["bank"] += amount
        embed = discord.Embed(
            title=f"Money given to {user} by {ctx.author}", colour=discord.Color.magenta())
        await ctx.reply(embed=embed)
        with open('mainbank.json', 'w') as f:
            json.dump(users, f)

    @commands.command(aliases=['rm'])
    @commands.has_permissions(administrator=True)
    async def removemoney(self, ctx, amount=None, user: discord.Member = None):
        if user == None:
            user = ctx.author
        elif amount == None:
            await ctx.reply("Enter the amount of money to be Removed")
            return
        await open_account(user)
        amount = int(amount)
        users = await get_bank_data()
        users[str(user.id)]["wallet"] -= amount
        embed = discord.Embed(
            title=f"Money taken from {user} by {ctx.author}", colour=discord.Color.magenta())
        await ctx.reply(embed=embed)
        with open('mainbank.json', 'w') as f:
            json.dump(users, f)

    @commands.command(aliases=["give", "moneygive", "givemoney", "send", "share", "pay"])
    async def sendmoney(self, ctx, member: discord.Member, amount=None):
        await open_account(ctx.author)
        await open_account(member)
        if amount == None:
            await ctx.send("Ok, you wanna tell me how much you want to withdraw now?")
            return

        bal = await update_bank(ctx.author)
        amount = int(amount)
        if amount == "all":
            amount = bal[0]

        if amount > bal[1]:
            await ctx.send("You don't have that much money")
            return

        if amount < 0:
            await ctx.send("amount must be postitive")
            return

        await update_bank(ctx.author, -1 * amount, "bank")
        await update_bank(member, amount, "bank")

        await ctx.send(f"You Gave {amount} of coins to {member}")

def setup(bot):
    bot.add_cog(Economy(bot))
