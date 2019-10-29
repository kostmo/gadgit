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
