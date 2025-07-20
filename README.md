# DiscordCappuccino

簡易な Discord Bot のサンプルです。`commands/` 以下の拡張を読み込み、スラッシュコマンドを中心に動作します。VOICEVOX を利用した読み上げ機能と、YouTube などの音源を再生する簡易音楽プレイヤーを搭載しています。

## フォルダ構成例

```
DiscordCappuccino/
├─ bot.py
├─ commands/
│  ├─ __init__.py
│  └─ ping.pyなど
├─ .env.example
└─ requirements.txt
```

## `.env.example` の記述例

```
DISCORD_BOT_TOKEN=YOUR_TOKEN_HERE
BOT_PREFIX=c!
SUPPORT_SERVER_URL=https://example.com/support
BOT_INVITE_URL=https://example.com/invite
VOICEVOX_URL=http://localhost:50021
...追加予定
```

ボットのタイムゾーンは起動後に `/setup` コマンドで指定します。

`.env.example` を `.env` にコピーしてトークンや各種 URL を編集してください。

## 起動手順

1. Python 3.10 以降を用意します。
2. 仮想環境を作成してアクティベートします。
3. `pip install -r requirements.txt` で依存をインストールします。
4. `.env.example` を `.env` にコピーし、`DISCORD_BOT_TOKEN` を設定します。
5. VOICEVOX エンジンを起動し、`VOICEVOX_URL` を設定します。
6. `python bot.py` を実行して起動します。

## コマンド追加ガイド

新しいコマンドは `commands/` ディレクトリに `xxx.py` を作成し、`Cog` クラスと `async def setup(bot)` を定義して追加します。

```
from discord.ext import commands

class Example(commands.Cog):
    ...

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Example(bot))
```

## 主な機能

- VOICEVOX によるテキスト読み上げ (`/join`, `/setvoice`, `/disconnect`, `/skip`)
- YouTube 等の音源再生 (`/play`, `/queue`, `/remove`, `/keep`, `/seek`, `/rewind`, `/forward`, `/stop`)

## FAQ

将来的に prefix を使用しない運用も可能なように、スラッシュコマンドを主体としています。`BOT_PREFIX` を空にするとプレフィックスコマンドを無効化できます。
プレフィックスコマンドが反応しない場合は Developer Portal で Message Content Intent を有効化してください。
