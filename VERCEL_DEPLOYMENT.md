# Vercel Deployment Guide

This guide provides instructions for testing the API locally and deploying it to Vercel.

## Local Testing

Before deploying to Vercel, it's important to test the API locally to ensure everything works as expected.

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Testing Scripts

We've provided several scripts to help you test the API locally:

1. **Basic Flask API Test**:
   ```bash
   python test_api_local.py
   ```
   This will start a Flask server on port 8000 and provide instructions for testing the endpoints.

2. **Automated API Tests**:
   ```bash
   python test_api_automated.py
   ```
   This script will automatically test all API endpoints and report the results.

3. **Vercel Handler Tests**:
   ```bash
   python test_vercel_handler.py
   ```
   This script simulates the Vercel serverless environment locally and tests the handler function.

4. **Run All Tests**:
   ```bash
   ./run_tests.sh
   ```
   This shell script will run all the tests and report the results.

### Manual Testing

You can also test the API manually using curl or a tool like Postman:

```bash
# Test the home endpoint
curl http://localhost:8000/

# Test the status endpoint
curl http://localhost:8000/status

# Test the query endpoint
curl -X POST -H "Content-Type: application/json" -d '{"message": "Hello"}' http://localhost:8000/query

# Test the analyze endpoint
curl -X POST -H "Content-Type: application/json" -d '{"token_id": "bitcoin"}' http://localhost:8000/analyze

# Test the technical endpoint
curl -X POST -H "Content-Type: application/json" -d '{"token_id": "bitcoin"}' http://localhost:8000/technical

# Test the whale endpoint
curl -X POST -H "Content-Type: application/json" -d '{"token_id": "bitcoin"}' http://localhost:8000/whale
```

## Deploying to Vercel

Once you've tested the API locally and everything works as expected, you can deploy it to Vercel.

### Prerequisites

- A Vercel account
- Vercel CLI (optional, for local deployments)

### Deployment Steps

1. **Push to GitHub**:
   Make sure your code is pushed to a GitHub repository.

2. **Connect to Vercel**:
   - Go to the Vercel dashboard (https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Configure the project:
     - Framework Preset: Other
     - Root Directory: ./
     - Build Command: None
     - Output Directory: None

3. **Configure Environment Variables**:
   - In the Vercel project settings, go to the "Environment Variables" section
   - Add any required environment variables (like API keys)
   - Make sure these are set for the Production environment

4. **Deploy**:
   - Click "Deploy"
   - Wait for the deployment to complete
   - Vercel will provide a URL for your application

### Testing the Deployment

After deployment, test your API using the provided Vercel URL:

```bash
# Test the home endpoint
curl https://your-vercel-app-url.vercel.app/

# Test the status endpoint
curl https://your-vercel-app-url.vercel.app/status

# Test the query endpoint
curl -X POST -H "Content-Type: application/json" -d '{"message": "Hello"}' https://your-vercel-app-url.vercel.app/query

# Test the analyze endpoint
curl -X POST -H "Content-Type: application/json" -d '{"token_id": "bitcoin"}' https://your-vercel-app-url.vercel.app/analyze

# Test the technical endpoint
curl -X POST -H "Content-Type: application/json" -d '{"token_id": "bitcoin"}' https://your-vercel-app-url.vercel.app/technical

# Test the whale endpoint
curl -X POST -H "Content-Type: application/json" -d '{"token_id": "bitcoin"}' https://your-vercel-app-url.vercel.app/whale
```

## Troubleshooting

If you encounter issues with your Vercel deployment, check the following:

1. **Runtime Logs**:
   - In the Vercel dashboard, go to the "Deployments" tab
   - Click on your deployment
   - Go to the "Runtime Logs" tab
   - Look for any errors or warnings

2. **Common Issues**:
   - **ImportError**: A required Python package is missing. Check your `api/requirements.txt` file.
   - **Environment Variables**: Make sure environment variables are configured on the Vercel dashboard.
   - **Memory Limits**: If you hit memory limits, you may need to increase the `maxLambdaSize` in `vercel.json`.

3. **Incremental Complexity**:
   After you have a successful basic deployment, you can start adding back the more complex parts of your application:
   - Add Dependencies: Add back the dependencies in `api/requirements.txt` (e.g., langchain-openai, etc.)
   - Reintroduce Environment Variables: After ensuring environment variables are correctly set in the Vercel dashboard
   - Integrate Trading Tools: Slowly re-integrate the crypto trading tools from the tools directory

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
- [Flask Documentation](https://flask.palletsprojects.com/) 