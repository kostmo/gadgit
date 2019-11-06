# Gadgit

Mirrors a Git repo to which web applications can make efficient queries
for information that the GitHub API does not provide.

## Demo

Serves [pytorch repo](http://gadgit.pytorch.org/)

## Features

### Event-driven repo maintenance

Keeps repo clone up-to-date by re-`fetch`ing upon GitHub `push` and `pull_request` events.

### Efficient information retrieval

* Bulk git commit metadata retrieval
* Queries
    * is-ancestor queries
    * merge base queries
    * Determine Pull Request with a given head commit
    * Determine head commit of a given Pull Request

### Diagnostics

* Logs all received GitHub events
* Logs all fetch operations

### Repo hosting

* uses a "bare" repo clone
* rate-limits new fetches to 1 per minute
* protects against simultaneous `fetch` or `clone` operations 

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

Exercise an endpoint with `curl`:

    curl --data '["0c7537c40939f7682c179813a4b7a50020f08152", "7ed9a3ec4895f0f501cf435fec88ff974d93f3da"]' http://localhost:5000/commit-metadata


