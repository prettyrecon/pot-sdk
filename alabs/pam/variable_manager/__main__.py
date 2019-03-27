from alabs.pam.variable_manager import VM_API_PORT, app


if __name__ == "__main__":
    api_port = VM_API_PORT
    if not api_port:
        raise RuntimeError('API_PORT environment variable is not set!')
    app.run(host="0.0.0.0", port=int(api_port), debug=True)
