from alabs.pam.la.bot.app import main
################################################################################
if __name__ == "__main__":
    # api_port = os.environ.get('VM_API_PORT')
    api_port = 8082
    if not api_port:
        raise RuntimeError('API_PORT environment variable is not set!')
    main()