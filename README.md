# Lyft Button API

This is the serverless API that backs avatar.jairtrejo.com. It uses:

- An AWS SAM template to describe the lambda functions and the API Gateway.
- A Python package with the actual code for the function.

## Running the API locally

Install the code to the `dist/` folder py calling:

```shell
$ pip install -t dist .
```

And then:

```shell
$ sam local start-api
```
