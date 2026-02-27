from flask import Flask, render_template, jsonify, request, redirect
import discord
from threading import Thread

def init_app(bot):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html", bot=bot)

    @app.route("/ping")
    def ping():
        return jsonify({"ping": round(bot.latency * 1000)})

    @app.route("/invite")
    def invite():
        return redirect(f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands")

    @app.route("/commands")
    def commands():
        return render_template("commands.html", bot=bot)

    @app.route("/execute_command", methods=["POST"])
    async def execute_command():
        data = request.get_json()
        command_name = data.get("command")
        args = data.get("args")
        guild_id = data.get("guild_id")
        
        guild = bot.get_guild(int(guild_id))
        if not guild:
            return jsonify({"status": "error", "message": "Guild not found"})

        command = bot.get_command(command_name)
        if not command:
            return jsonify({"status": "error", "message": "Command not found"})

        # This is a simplified example. In a real application, you would need to handle permissions and context.
        # For security reasons, this is not a recommended way to execute commands.
        # You should implement proper authentication and authorization.
        
        # Create a dummy context
        # NOTE: This is a hack and might not work for all commands.
        # It's better to find a way to get a real context.
        channel = guild.text_channels[0] # Get the first text channel
        message = await channel.send(f"!{command_name} {args}")
        ctx = await bot.get_context(message)
        
        try:
            await command(ctx, *args.split())
            return jsonify({"status": "success", "message": "Command executed"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    def run():
        app.run(host='0.0.0.0', port=8080)

    thread = Thread(target=run)
    thread.start()