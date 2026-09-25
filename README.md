# QQ Tiny Things Bot

## Setup

1. Create a QQ bot app in QQ Open Platform and enable the at-message event you need.
2. Copy `.env.example` to `.env`, then fill in `QQ_APP_ID` and `QQ_APP_SECRET`.
3. Run `python -m pip install -r requirements.txt`.
4. Run `python bot.py`.

The first start creates `bot.db`. It holds Bo Bing games and player prize records. Do not commit `.env` or `bot.db`.

## Commands

Commands can be sent after mentioning the bot. If your QQ bot is configured as a private-guild bot and the `guild_messages` intent is approved, channel messages can also be sent without an @ mention.

| Command | Description |
| --- | --- |
| `/help`, `/帮助`, `help`, or `帮助` | Show the command list. |
| `/ck [1-50]` or `/抽卡 [1-50]` | Draw cute little items. The default is one draw. |
| `/bond` or `/羁绊` | Generate a playful bond result with a random group member. |
| `/bond add 小红` or `/羁绊 add 小红` | Add yourself to this group's bond roster with a display name. |
| `/bond remove 小红` or `/羁绊 remove 小红` | Remove a display name from this group's bond roster. |
| `/bond list` or `/羁绊 list` | Show this group's bond roster, the registered names used for matching. |

When a user @mentions the bot, it also records the nickname provided by QQ into the bond roster when available. Manual `/bond add` registration remains the most reliable option because QQ group events may omit nicknames.
| `/task` or `/任务` | Generate a random group task, with many emoji challenges. |
| `/task status` or `/任务 状态` | Show the active verified emoji challenge. |
| `/task ans` or `/任务 答案` | Show the previous emoji challenge answer. |
| `/task cancel` or `/任务 取消` | Cancel your active emoji challenge. |
| `/game list` or `/game help` | List available games. |
| `/game 1` | Start the emoji theme task. |
| `/game 2` | Start the untimed Emoji phrase guessing game. |
| `/game 3` | Start the AI two-character noun guessing game; guess with `? 两字词`. |
| `/game 3 hint` | Ask AI for a clue without revealing the answer. |
| `/game 3 ans` | Ask AI to reveal the answer and end the game. |
| `/game 4` | Start the local two-character noun guessing game without AI. |
| `/game ans` | Show the answer to the previous game question. |
| `/game ans 冬日小屋` | Show the candidate Emoji for a named game 1 theme. |
| `/game re` or `/game restart` | Restart the current game. |
| `/game end` | End the current game. |
| `/achievement` or `/成就` | Show achievement progress. |
| `/collection` or `/图鉴` | Show your draw collection and hidden-item progress. |
| `/ai 问题` or `/问 问题` | Ask DeepSeek through its web chat page. |
| `/name 小红` or `/昵称 小红` | Manually set a display name used by the bond feature if QQ does not provide one. |
| `/bb` or `/博饼` | Roll six dice and show the result. This is a free roll and does not consume a game prize. |
| `/bb start` or `/博饼 start` | Start one Bo Bing match for the current group/channel. Only one match can be active there. |
| `/bb status` or `/博饼 状态` | Show the active match's remaining prizes and personal prize record. |
| `/bb end` or `/博饼 结束` | End the active match. The match starter can end it. |
| `/bb state [1|2]` or `/博饼 state [1|2]` | Set classic number dice (1) or Unicode dice symbols (2). Omit the number to toggle. |

In a match, use `/bb` or `/博饼` to roll. A winning roll receives the highest still-available prize tier it qualifies for. One active match has 63 prizes: Zhuangyuan x1, Duutangyuan x2, Santangyuan x4, Sitongxiu x8, Erju x16, and Yixiu x32.

When a player rolls Zhuangyuan, their name is appended to the Zhuangyuan list. Zhuangyuan rolls have equal rank and the first player listed wins the final settlement. When all prizes are gone, the match announces the final Zhuangyuan.

## Draw Pool

`data/rewards.json` contains 300 draw records: 270 regular cute items plus 30 hidden items. Hidden items collectively have a 10% draw chance and are uniformly selected when that chance triggers.

## DeepSeek Web Chat

1. Install dependencies with `python -m pip install -r requirements.txt`.
2. Install Chromium with `python -m playwright install chromium`.
3. In `.env`, set `DEEPSEEK_WEB_ENABLED=true` and keep `DEEPSEEK_WEB_HEADLESS=false` for the first launch.
4. Start the bot. Chromium opens DeepSeek when the first `/ai` request arrives. Log in there; the local `browser-profile/` folder retains the session.

After login, @mention the bot to chat with AI. Ordinary group messages are ignored, except when the task creator submits a matching Emoji sequence for an active themed task. Each group uses its own DeepSeek browser tab and keeps an independent conversation context. Requests are processed one at a time. The browser profile is sensitive and is ignored by Git.
