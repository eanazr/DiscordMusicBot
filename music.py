import discord
from discord.ext import commands
import youtube_dl

class music(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.song_queue = {}
    self.queue_info = []

  @commands.Cog.listener()
  async def on_ready(self):
    for guild in self.client.guilds:
      self.song_queue[guild.id] = []

  async def check_queue(self, ctx):
    if len(self.song_queue[ctx.guild.id]) > 0:
      ctx.voice_client.stop()
      await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
      await ctx.send("I'll start playing {0}".format(self.queue_info[0])  + " ✨")
      
      try:
        self.song_queue[ctx.guild.id].pop(0)
        self.queue_info.pop(0)
      except:
        await ctx.voice_client.disconnect()

  @commands.command()
  async def join(self,ctx):
    if ctx.author.voice is None:
        await ctx.send("Can't hear you~! Join a voice channel first.")
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)

  @commands.command(aliases=['s'])
  async def skip(self,ctx):
    await ctx.send("Playing next song! ⏩")
    ctx.voice_client.stop()

  @commands.command()
  async def pause(self,ctx):
    await ctx.send("Taking a break~ ⏸")
    await ctx.voice_client.pause()

  @commands.command()
  async def resume(self,ctx):
    await ctx.send("I'll start playing again! ▶")
    await ctx.voice_client.resume()

  @commands.command(aliases=['dc'])
  async def disconnect(self,ctx):
    ctx.voice_client.stop()
    await self.clear(ctx)
    await ctx.voice_client.disconnect()

  @commands.command(aliases=['p','mainkan'])
  async def play(self,ctx,*,url):
    if ctx.voice_client is None:
      await self.join(ctx)

    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
      info = ydl.extract_info(f"ytsearch:{url}", download=False)
      if 'entries' in info:
        url2 = info["entries"][0]["formats"][0]['url']
      elif 'formats' in info:
        url2 = info["formats"][0]['url']

      song = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
      embed_url = info["entries"][0]["webpage_url"]
      embed_name = info["entries"][0]["title"]
      embed = embed_url + " - " + embed_name
      
      if ctx.voice_client.source is not None:
        queue_len = len(self.song_queue[ctx.guild.id])
        self.song_queue[ctx.guild.id].append(song)
        self.queue_info.append(embed)
        print(self.queue_info)
        await ctx.send("I'm adding {0}".format(embed_name) + " to queue number {0}".format(queue_len+1))

      await self.play_song(ctx, song)
      await ctx.send("I'll start playing {0}".format(embed) + " ✨")

  async def play_song(self, ctx, song):
    vc = ctx.voice_client
    vc.play(song, after=lambda error: self.client.loop.create_task(self.check_queue(ctx)))

  @commands.command(aliases=['l'])
  async def list(self, ctx):
    if len(self.queue_info) == 0:
      return await ctx.send("Queue is empty")
    else:
      embed = discord.Embed(title="Song Queue", description="", colour=discord.Colour.blue())
      i = 1
      for info in self.queue_info:
        embed.description += f"{i}) {info}\n"
        i += 1
      await ctx.send(embed=embed)

  @commands.command(aliases=['cl'])
  async def clear(self, ctx):
    i = 0
    while i < len(self.song_queue[ctx.guild.id]):
      self.song_queue[ctx.guild.id].pop(0)
      self.queue_info.pop(0)

def setup(client):
  client.add_cog(music(client))
