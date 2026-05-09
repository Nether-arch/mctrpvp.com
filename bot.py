import discord
from discord.ext import commands, tasks
from google import genai
import random
import asyncio
import os

# ── Config ──────────────────────────────────────────────────────────────────
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID          = 1499378375305728020
CHANNEL_ID        = 1502698586431815892
LOG_CHANNEL_ID    = 1501651214138474536
GOOGLE_API_KEY    = os.getenv("GOOGLE_API_KEY")

# ── Gemini Setup ─────────────────────────────────────────────────────────────
client = genai.Client(api_key=GOOGLE_API_KEY)

SYSTEM_PROMPT = """Sen MCTRPVP adlı bir Discord botusun. Minecraft PvP sunucusuna ait, sert ve rekabetçi bir karakterin var.
Türkçe konuş. Kısa, etkili cevaplar ver. Şu konularda uzmansın:
- Minecraft PvP teknikleri (knockback, sprint reset, w-tapping, strafing)
- Kit PvP, UHC, Crystal PvP, Sword PvP
- İyi PvP gear ve enchantment önerileri  
- Combo yapmak, clutch etmek
- Rakipleri ezme ve dominant olma
- PvP motivasyonu ve mentalitesi
Her zaman güvenli, rekabetçi ve heyecanlı bir dil kullan. Rakipleri "bot", "noob", "ez" gibi PvP kültürüne uygun terimlerle aşağılayabilirsin.
Emoji kullan ⚔️🔥💀🏆
"""

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
intents.members = True
intents.presences = True


bot = commands.Bot(command_prefix="!", intents=intents)

conversation_history: dict[int, list] = {}  # user_id -> chat history

# ── Gemini Chat Helper ────────────────────────────────────────────────────────
async def ask_gemini(user_id: int, user_message: str) -> str:
    try:
        if user_id not in conversation_history:
            conversation_history[user_id] = []

        history = conversation_history[user_id]
        history.append(f"Kullanıcı: {user_message}")

        # Son 10 mesajı hafızada tut
        context = "\n".join(history[-10:])
        full_prompt = SYSTEM_PROMPT + "\n\nKonuşma geçmişi:\n" + context + "\n\nBot:"

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt
            )
        )
        reply = response.text.strip()
        history.append(f"Bot: {reply}")
        return reply
    except Exception as e:
        return f"⚠️ Bir hata oluştu: {str(e)}"

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
            "⚔️ **MCTRPVP Bot aktif!** Hazır mısınız? PvP sezonu açıldı! "
            "Bana soru sormak için `!pvp <soru>` yaz veya doğrudan mention at. 🔥"
        )

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    # Bot mention edilirse veya hedef kanalda mesaj atılırsa yanıt ver
    mentioned = bot.user in message.mentions
    in_target = message.channel.id == CHANNEL_ID

    if (mentioned or in_target) and not message.content.startswith("!"):
        content = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if not content:
            return

        async with message.channel.typing():
            reply = await ask_gemini(message.author.id, content)
        await message.reply(reply)

# ── Commands ──────────────────────────────────────────────────────────────────
@bot.command(name="pvp")
async def pvp_cmd(ctx, *, soru: str = None):
    """AI destekli PvP sorusu sor: !pvp <soru>"""
    if not soru:
        await ctx.reply("❓ Bir soru sor! Örnek: `!pvp nasıl daha iyi combo atarım?`")
        return
    async with ctx.typing():
        reply = await ask_gemini(ctx.author.id, soru)
    await ctx.reply(reply)

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
    embed.add_field(name="!pvp <soru>",   value="AI ile PvP sorusu sor",        inline=False)
    embed.add_field(name="!ipucu",         value="Rastgele PvP ipucu al",        inline=False)
    embed.add_field(name="!stats [@kişi]", value="PvP istatistiklerini gör",     inline=False)
    embed.add_field(name="!duello @kişi",  value="Birine 1v1 daveti gönder",     inline=False)
    embed.add_field(
        name="!test @oyuncu <mc_nick> <yeni_tier> <eski_tier> <kit>",
        value="Test sonucu log kanalına kaydet\nÖrn: `!test @emirhan Heid4uk4HD LT5 Unranked mace`",
        inline=False
    )
    embed.add_field(name="@MCTRPVP <msg>", value="Botla sohbet et (AI destekli)", inline=False)
    embed.set_footer(text="MCTRPVP | Efsaneler Burada Yazılır 🏆")
    await ctx.send(embed=embed)

# ── Run ───────────────────────────────────────────────────────────────────────
bot.run(DISCORD_BOT_TOKEN)