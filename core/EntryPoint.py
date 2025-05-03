from core.Application import Application

def main(application: Application):
    """
    Main entry point for the application.
    """
    # Initialize the application
    application.on_start()

    # Run the main loop
    application.run()