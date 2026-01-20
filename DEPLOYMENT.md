# Deployment Guide 🚀

Follow these steps to deploy your **Free RAG System** to the cloud.

## Prerequisites
1.  **GitHub Account**: Push your code to a new public/private repository.
2.  **Render Account**: Sign up at [render.com](https://render.com).
3.  **Groq & Pinecone Keys**: Have your `.env` values ready.

## Step 1: Deploy to Render (Backend + Frontend)

1.  Go to the **Render Dashboard**.
2.  Click **New +** -> **Blueprint**.
3.  Connect your GitHub repository.
4.  Render will detect `render.yaml`. Click **Apply**.
5.  **Environment Variables**: You MUST manually add these in the Render Dashboard for the `rag-backend` service:
    *   `GROQ_API_KEY`: (Your key)
    *   `PINECONE_API_KEY`: (Your key)
    *   `PINECONE_ENV`: (e.g., us-east-1)
    *   `PINECONE_INDEX_NAME`: `rag-agent` (or your index name)
    *   `EMBEDDING_PROVIDER`: `local` (keeps it free)
    *   `LLM_PROVIDER`: `groq`

6.  Click **Save Changes**. Render will start building.
    *   *Note: First build takes ~5 mins.*

## Step 2: Set up the Keep-Alive (Cron Job)

1.  Once deployed, copy your **Backend URL** (e.g., `https://rag-backend-xyz.onrender.com`).
2.  In your code on your PC, open `.github/workflows/keep_alive.yml`.
3.  Replace the placeholder URL with your actual Render URL:
    ```yaml
    curl -I https://rag-backend-xyz.onrender.com/api/metrics/recent
    ```
4.  Commit and Push this change to GitHub.
5.  Go to your GitHub Repo -> **Actions** tab. You should see "Keep Render Alive" workflow. It will run automatically every 14 minutes.

## Done! 🎉
Your app is now live 24/7 for free!
