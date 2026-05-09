import discord
from discord.ext import commands, tasks
import random
import os

# ── Config ──────────────────────────────────────────────────────────────────
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID          = 1499378375305728020
CHANNEL_ID        = 1502698586431815892
LOG_CHANNEL_ID    = 1501651214138474536

# ── Otomatik mesajlar ────────────────────────────────────────────────────────
AUTO_MESSAGES = [
    "⚔️ Kimse bana meydan okumaya cesaret edemiyor mu? **1v1 kabul ediyorum!**",
    "🔥 PvP pratiği yapmayan yerinde sayar. Her gün sword sallamak şart!",
    "💀 Son düşürdüğüm adam ekranın başında ağlamış olmalı 😂",
    "🏆 **MCTRPVP** klanı olarak rakipleri ezmeye devam ediyoruz!",
    "⚔️ Crystal PvP bilen var mı? Bugün workshop açıyorum, gelin öğrenin!",
    "🔥 W-tap öğrenmeden PvP oynanmaz. Bunu bilmeyenler bot sayılır.",
    "💥 Sprint reset atmadan combo yapmaya çalışanları tanıyorum... **Hepsini düşürdüm.**",
    "🗡️ Strafing + knockback hesabı = ölümsüz combo. Bunu çözdünüz mü?",
    "🎯 Bugün kaç kişi düşürdünüz? Benim sayım: **bilmiyorum artık saymayı bıraktım.**",
    "👑 **Rank #1** olmak için çalışıyoruz. Siz ne yapıyorsunuz?",
]

# ── Bot Setup ─────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ── Otomatik mesaj görevi ─────────────────────────────────────────────────────
@tasks.loop(minutes=30)
async def auto_pvp_message():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        msg = random.choice(AUTO_MESSAGES)
        await channel.send(msg)

# ── Events ────────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ {bot.user} olarak giriş yapıldı!")
    print(f"📡 Sunucu: {GUILD_ID} | Kanal: {CHANNEL_ID}")
    auto_pvp_message.start()

    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(
            "⚔️ **MCTRPVP Bot aktif!** Hazır mısınız? PvP sezonu açıldı! 🔥"
        )

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    await bot.process_commands(message)

# ── Commands ──────────────────────────────────────────────────────────────────
@bot.command(name="ipucu")
async def ipucu_cmd(ctx):
    """Rastgele PvP ipucu verir"""
    ipuclari = [
        "⚔️ **W-Tap:** Her vuruştan sonra W tuşunu bırak ve bas. Sprint resetler ve daha çok knockback yapar!",
        "🎯 **Strafing:** Rakibinin etrafında A-D tuşlarıyla sürekli hareket et. Vurması zorlaşır.",
        "💥 **Sprint Reset:** Vururken sprint'i kapat/aç. Critical hit şansı ve KB artar.",
        "🛡️ **Blocking:** Kılıçla sağ tıkla, hasar %50 azalır. Tam zamanında kullan!",
        "🏃 **Rodning:** Balık oltasıyla rakibi çek, combo'yu kapat. Efsane teknik!",
        "💎 **Enchant Öneri:** Sword için Sharpness 5 + Fire Aspect 2 + Looting 3 şart!",
        "🧠 **Mentalite:** Ölünce paniğe kapılma. Her ölüm bir ders. Sakin kal, comeback yap.",
        "🎮 **CPS:** Saniyede 8-12 tık ideal. Çok fazla CPS knockback'i bozar, dikkat!",
    ]
    await ctx.send(random.choice(ipuclari))

@bot.command(name="stats")
async def stats_cmd(ctx, kullanici: discord.Member = None):
    """Eğlenceli PvP istatistikleri göster"""
    hedef = kullanici or ctx.author
    kills = random.randint(50, 9999)
    deaths = random.randint(1, kills // 2)
    kd = round(kills / max(deaths, 1), 2)
    streak = random.randint(1, 50)

    embed = discord.Embed(
        title=f"⚔️ {hedef.display_name} — PvP İstatistikleri",
        color=discord.Color.red()
    )
    embed.add_field(name="💀 Kill", value=str(kills), inline=True)
    embed.add_field(name="☠️ Ölüm", value=str(deaths), inline=True)
    embed.add_field(name="📊 K/D", value=str(kd), inline=True)
    embed.add_field(name="🔥 En Uzun Seri", value=str(streak), inline=True)
    embed.set_footer(text="MCTRPVP | Efsaneler Burada Yazılır")
    embed.set_thumbnail(url=hedef.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="duello")
async def duello_cmd(ctx, rakip: discord.Member = None):
    """Birine düello meydan oku!"""
    if not rakip:
        await ctx.reply("❓ Kime meydan okuyorsun? `!duello @kullanici`")
        return
    if rakip.bot:
        await ctx.reply("🤖 Bota meydan okuyamazsın, o zaten bot! Gerçek bir rakip bul.")
        return

    embed = discord.Embed(
        title="⚔️ DÜELLO DAVETI!",
        description=f"🔥 **{ctx.author.display_name}** seni **1v1'e** davet ediyor, {rakip.mention}!\n\n"
                    f"Kabul edecek misin yoksa kaçacak mısın? 💀",
        color=discord.Color.dark_red()
    )
    embed.set_footer(text="MCTRPVP | Korkaklara yer yok!")
    await ctx.send(embed=embed)

@bot.command(name="test")
async def test_cmd(ctx,
                   oyuncu: discord.Member = None,
                   mc_nick: str = None,
                   yeni_tier: str = None,
                   eski_tier: str = None,
                   kit: str = None):
    """
    Test sonucu kaydeder ve log kanalına gönderir.
    Kullanım: !test @oyuncu <mc_nick> <yeni_tier> <eski_tier> <kit>
    Örnek:    !test @emirhan Heid4uk4HD LT5 Unranked mace
    """
    # Eksik parametre kontrolü
    if not all([oyuncu, mc_nick, yeni_tier, eski_tier, kit]):
        embed = discord.Embed(
            title="❌ Eksik Parametre",
            description=(
                "**Doğru kullanım:**\n"
                "`!test @oyuncu <mc_nick> <yeni_tier> <eski_tier> <kit>`\n\n"
                "**Örnek:**\n"
                "`!test @emirhan Heid4uk4HD LT5 Unranked mace`"
            ),
            color=discord.Color.red()
        )
        await ctx.reply(embed=embed)
        return

    # Tier'a göre renk
    tier_renkler = {
        "HT1": 0xFFD700, "HT2": 0xFFD700, "HT3": 0xFFD700,
        "LT1": 0xC0C0C0, "LT2": 0xC0C0C0, "LT3": 0xC0C0C0,
        "LT4": 0xC0C0C0, "LT5": 0xC0C0C0,
        "A":   0x3498DB, "B":   0x2ECC71, "C":   0xE67E22,
        "D":   0xE74C3C, "Unranked": 0x95A5A6,
    }
    renk = tier_renkler.get(yeni_tier, 0xFF4444)

    # Minecraft baş resmi (mc-heads.net)
    mc_avatar = f"https://mc-heads.net/avatar/{mc_nick}/64"

    embed = discord.Embed(
        title=f"{oyuncu.display_name} için Test Sonucu",
        color=renk
    )
    embed.add_field(name="🎮 Oyuncu",   value=oyuncu.mention,       inline=True)
    embed.add_field(name="🔧 Tester",   value=ctx.author.mention,   inline=True)
    embed.add_field(name="⬜ MC Nick",  value=f"`{mc_nick}`",        inline=False)
    embed.add_field(name="🏆 Yeni Tier", value=f"**{yeni_tier}**",  inline=True)
    embed.add_field(name="📋 Eski Tier", value=f"**{eski_tier}**",  inline=True)
    embed.add_field(name="🎯 Kit",       value=f"`{kit}`",           inline=True)
    embed.set_thumbnail(url=mc_avatar)
    embed.set_footer(text="Log Sistemi")
    embed.timestamp = discord.utils.utcnow()

    # Log kanalına gönder
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(embed=embed)
        await ctx.reply(f"✅ Test sonucu **#{log_channel.name}** kanalına kaydedildi!")
    else:
        await ctx.send(embed=embed)
        await ctx.reply("⚠️ Log kanalı bulunamadı, buraya gönderildi.")


@bot.command(name="yardim")
async def yardim_cmd(ctx):
    """Tüm komutları listele"""
    embed = discord.Embed(
        title="⚔️ MCTRPVP Bot Komutları",
        color=discord.Color.red()
    )
    embed.add_field(name="!ipucu",         value="Rastgele PvP ipucu al",        inline=False)
    embed.add_field(name="!stats [@kişi]", value="PvP istatistiklerini gör",     inline=False)
    embed.add_field(name="!duello @kişi",  value="Birine 1v1 daveti gönder",     inline=False)
    embed.add_field(
        name="!test @oyuncu <mc_nick> <yeni_tier> <eski_tier> <kit>",
        value="Test sonucu log kanalına kaydet\nÖrn: `!test @emirhan Heid4uk4HD LT5 Unranked mace`",
        inline=False
    )
    embed.set_footer(text="MCTRPVP | Efsaneler Burada Yazılır 🏆")
    await ctx.send(embed=embed)

# ── Run ───────────────────────────────────────────────────────────────────────
bot.run(DISCORD_BOT_TOKEN)
