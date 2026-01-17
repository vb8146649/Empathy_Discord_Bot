import discord
import os
from dotenv import load_dotenv
from agents import EmpathySystem

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True 

client = discord.Client(intents=intents)
system = EmpathySystem()

# --- 🧠 MEMORY STORAGE ---
# Stores pending suggestions. 
# Format: { user_id: { 'channel_id': 123, 'suggestion': "The nice text" } }
pending_suggestions = {} 

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}. Waiting for toxicity...')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # --- CASE 1: USER REPLIES "YES" IN DMs ---
    if isinstance(message.channel, discord.DMChannel):
        if message.content.strip().upper() == "YES":
            user_id = message.author.id
            
            # Check if this user has a pending rewrite
            if user_id in pending_suggestions:
                data = pending_suggestions[user_id]
                target_channel = client.get_channel(data['channel_id'])
                suggestion = data['suggestion']
                
                if target_channel:
                    # Send the nice message to the public channel
                    await target_channel.send(f"**{message.author.display_name}:** {suggestion}")
                    await message.channel.send("✅ Awesome! I posted that for you.")
                    
                    # Clear memory
                    del pending_suggestions[user_id]
                else:
                    await message.channel.send("❌ Error: I can't find the original channel anymore.")
            else:
                await message.channel.send("I don't have any pending suggestions for you right now.")
        return

    # --- CASE 2: PUBLIC CHAT MONITORING ---
    # Only analyze if it's NOT a DM
    if not isinstance(message.channel, discord.DMChannel):
        
        # 1. Watcher Check
        analysis = await system.agent_watcher(message.content)

        if analysis.is_toxic:
            print(f"🚨 Toxic message detected from {message.author}")

            # Delete the toxic message
            try:
                await message.delete()
            except discord.Forbidden:
                print("Error: Need 'Manage Messages' permission.")

            # 2. Diplomat Rewrite
            rewrite = await system.agent_diplomat(message.content)

            # 3. Save to Memory
            pending_suggestions[message.author.id] = {
                'channel_id': message.channel.id,
                'suggestion': rewrite
            }

            # 4. Coach DM
            coach_msg = await system.agent_coach(message.content, rewrite)
            
            try:
                dm_channel = await message.author.create_dm()
                
                embed = discord.Embed(title="🛡️ Message Paused", color=0xFF5733)
                embed.description = coach_msg
                embed.add_field(name="Your Message", value=f"||{message.content}||", inline=False)
                embed.add_field(name="Suggested Alternative", value=rewrite, inline=False)
                embed.set_footer(text="Reply 'YES' to send the suggestion automatically.")
                
                await dm_channel.send(embed=embed)
                
                # Notify public channel briefly
                await message.channel.send(
                    f"🛡️ {message.author.mention}, let's take a breath. Check your DMs.", 
                    delete_after=5
                )
                
            except Exception as e:
                print(f"Could not DM user: {e}")

client.run(TOKEN)