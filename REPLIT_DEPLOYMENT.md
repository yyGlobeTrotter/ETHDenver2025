# Replit Deployment Guide for VinRouge-Dexy-Bot

This document provides instructions for deploying the VinRouge-Dexy-Bot on Replit.

## Configuration Files

The following files have been added to support Replit deployment:

1. `.replit` - Configures how Replit runs the application
2. `replit.nix` - Specifies the Nix packages required for the environment
3. `.replitignore` - Specifies files to be ignored by Replit

## Environment Variables

Make sure to set up the following environment variables in the Replit Secrets tab (lock icon):

- `OPENAI_API_KEY` - Your OpenAI API key
- Any other environment variables required by your application

## Running the Application

The application is configured to run using `server.py` as the entry point. Replit will automatically:

1. Install the dependencies from `requirements.txt`
2. Run the application using `python server.py`

## Web Preview Configuration

The `.replit` file includes configuration for the web preview:

```toml
[http_service]
internal_port = 8080
external_port = 80
url = "https://${REPL_SLUG}.${REPL_OWNER}.repl.co"
```

This tells Replit to:
- Look for a web server running on port 8080 inside the container
- Expose it on port 80 externally
- Use the standard Replit URL format for accessing the app

## Troubleshooting

If you encounter issues:

1. **No webpage to preview**:
   - Check if the server is running on port 8080 (set by the PORT environment variable)
   - Verify that the app is binding to `0.0.0.0` and not `localhost` or `127.0.0.1`
   - Try running the test file with `python test_replit.py` to see if a simple server works
   - Check the console for any error messages

2. **Environment variables**:
   - Verify that all required environment variables are set in the Secrets tab
   - The PORT environment variable is set to 8080 in the .replit file

3. **Dependencies**:
   - Make sure all dependencies are properly installed
   - Try running `pip install -r requirements.txt` in the Shell

4. **Port conflicts**:
   - If there's a port conflict, try changing the port in both the .replit file and server.py

## Notes

- Replit will automatically assign a port for your application, which is accessible via the `PORT` environment variable
- The application is configured to listen on `0.0.0.0` to be accessible from outside the Replit environment
- If you need to test with a simpler setup, use the included `test_replit.py` file 