# Gadgit

Mirrors a Git repo to which web applications can make efficient queries for branch ancestry/merge bases that the GitHub API does not provide.

## Deployment

Intended for hosting on Elastic Beanstalk.

Use this command to set the GitHub webhook secret:

    eb setenv GITHUB_WEBHOOK_SECRET=your_secret

To deploy the application, run:

    ./deploy.sh

### Webhook

Set up a GitHub webhook to post to `http://gadgit.pytorch.org/github-webhook-event` upon pushes.
This will trigger a re-fetch of the relevant refs.

## Testing

### Local

Run:

    eb-flask/application.py

Excercise an endpoint with `curl`:

    curl --data '["0c7537c40939f7682c179813a4b7a50020f08152", "7ed9a3ec4895f0f501cf435fec88ff974d93f3da"]' http://localhost:5000/commit-metadata


