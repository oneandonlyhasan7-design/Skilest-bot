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

    #
    # The /execute_command endpoint has been disabled due to a critical security vulnerability.
    # This endpoint allowed unauthenticated users to execute arbitrary commands on your bot,
    # which is a major security risk.
    #
    # To re-enable this functionality safely, you must implement the following:
    #   1. Authentication: Verify the identity of the user making the request.
    #   2. Authorization: Check if the authenticated user has permission to execute the command.
    #   3. Secure Context Creation: Properly create a command context instead of using a hacky method.
    #   4. Asynchronous Execution: Use a proper async web framework (like Quart, which is already in your
    #      requirements) and handle the interaction with the bot's event loop correctly.
    #
    # @app.route("/execute_command", methods=["POST"])
    # async def execute_command():
    #     data = request.get_json()
    #     command_name = data.get("command")
    #     args = data.get("args")
    #     guild_id = data.get("guild_id")
    #     
    #     guild = bot.get_guild(int(guild_id))
    #     if not guild:
    #         return jsonify({"status": "error", "message": "Guild not found"})
    #
    #     command = bot.get_command(command_name)
    #     if not command:
    #         return jsonify({"status": "error", "message": "Command not found"})
    #
    #     # This is a simplified example. In a real application, you would need to handle permissions and context.
    #     # For security reasons, this is not a recommended way to execute commands.
    #     # You should implement proper authentication and authorization.
    #     
    #     # Create a dummy context
    #     # NOTE: This is a hack and might not work for all commands.
    #     # It's better to find a way to get a real context.
    #     channel = guild.text_channels[0] # Get the first text channel
    #     message = await channel.send(f"!{command_name} {args}")
    #     ctx = await bot.get_context(message)
    #     
    #     try:
    #         await command(ctx, *args.split())
    #         return jsonify({"status": "success", "message": "Command executed"})
    #     except Exception as e:
    #         return jsonify({"status": "error", "message": str(e)})

    def run():
        app.run(host='0.0.0.0', port=8080)

    thread = Thread(target=run)
    thread.start()
