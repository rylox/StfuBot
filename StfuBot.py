import re
import discord


def is_valid_ipv4(data):
    regex = re.compile(r'(?:^|\b(?<!\.))(?:1?\d?\d|2[0-4]\d|25[0-5])(?:\.(?:1?\d?\d|2[0-4]\d|25[0-5])){3}(?=$|[^\w.])')
    return re.search(regex, data)


class Bot(discord.Client):

    def __init__(self, **options):
        super().__init__(**options)
        self.currently_tracked = None
        self.voice_client = None

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        game = discord.Game('shut the fuck up')
        await self.change_presence(status=discord.Status.online, activity=game)

    async def on_message(self, message):
        if message.author == self.user:
            await message.delete(delay=5.0)
            return

        if is_valid_ipv4(message.content):
            msg = '{0.author.mention} stfu'.format(message)
            self.currently_tracked = message.author
            await message.channel.send(msg)
            await message.delete()

            voice_state = message.author.voice
            if voice_state is not None:
                self.voice_client = await voice_state.channel.connect()
                await self.play_file()

    async def on_voice_state_update(self, member, before, after):
        if member == self.user:
            return

        if member == self.currently_tracked:
            if after.channel is not None and after.channel is not self.voice_client.channel:
                await self.voice_client.move_to(after.channel)

            if after.channel is None:
                self.currently_tracked = None

                if self.voice_client.is_playing():
                    self.voice_client.stop()

                await self.voice_client.disconnect()

    async def play_file(self):
        if self.voice_client is not None:
            source = await discord.FFmpegOpusAudio.from_probe("stfu.mp3")
            self.voice_client.play(source)


def main():
    bot = Bot()
    with open('token.txt') as f:
        token = f.read()
    bot.run(token)


if __name__ == '__main__':
    main()
