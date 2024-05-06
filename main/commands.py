from . import main

@main.cli.command('custom_command')
def custom_command():
    print("This is a custom command")