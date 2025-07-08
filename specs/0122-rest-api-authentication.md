- Feature Name: API Authentication
- Created: 2025-06-20
- Associated Issue: #2502

# Summary

Introduce a personal access token (PAT) implementation for accessing certain public-facing REST API endpoints in Pontoon.

# Motivation

There is an increasing need to protect or restrict access to specific endpoints using authentication.

This feature sets a standard for third parties and localizers by providing a more secure method of accessing Pontoon's external REST API. It also lays the groundwork for future enhancements, such as permission levels based on token access scope.

# Feature Explanation

## Features of a Personal Access Token (PAT)

The PAT implementation includes the following features:

- Tokens are created from the user settings page  
- Tokens have an expiration date  
- Users can hold up to 10 tokens simultaneously  
- Tokens can be deleted, but their values cannot be viewed again after the initial creation  
- Admins can monitor token usage and revoke tokens if necessary  
- A user’s Pontoon permissions determine what their token can access

## Creating, Viewing, and Deleting a Personal Access Token

A new **Personal Access Tokens** section will appear in the Settings page. A **Generate a New Access Token** button will allow users to create a new token, which is appended to a list (maximum of 10). Users can optionally add an expiration date and a note to each token to help identify its purpose.

After generation, the token is displayed once for the user to copy. Refreshing the page or navigating away will hide the token permanently.

Users can delete any of their existing tokens at any time.

## Using a Personal Access Token

To access protected external REST API endpoints at `https://pontoon.com/api/v2/`, users must attach a valid token to the `Authorization` header.

For example, to access the `/api/v2/resource/` endpoint:

```bash
curl \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  https://example.com/api/v2/resource/
```


### Incorrect Usage

If a user tries to access a protected endpoint without a valid token or without sufficient permissions, a `403 Unauthorized` response is returned.

Multiple consecutive failed attempts will result in the user's IP address being temporarily blocked.

## Admin Usage

Admins have access to the [`Django Admin Dashboard`](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/), where they can view token usage, usernames, and revoke tokens as needed.

When a token is revoked, the associated user receives a notification indicating its revocation, along with corresponding updates to their list of tokens.