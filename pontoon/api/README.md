# Pontoon Application Programming Interface

Pontoon provides a set of [RESTful](https://developer.mozilla.org/en-US/docs/Glossary/REST) endpoints via the [Django REST Framework](https://www.django-rest-framework.org/), accessible under `/api/v2/`.

## Authentication

Most endpoints are publicly accessible and require no authentication. A few endpoints require an authenticated user.

Requests can be authenticated either with a session cookie or with a Personal Access Token (PAT). You can create a PAT from your [user settings](https://pontoon.mozilla.org/settings/) page (see the [User Accounts & Settings](https://github.com/mozilla/pontoon/blob/main/documentation/docs/localizer/users.md#personal-access-tokens) documentation for details).

Send the token in the `Authorization` header using the `Bearer` scheme:

```bash
$ curl \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  "https://example.com/api/v2/pretranslate/"
```

A PAT automatically expires one year after it is created, and can be deleted manually at any time. Requests made with an invalid or expired token are rejected.

## JSON Mode

When a request is sent without any headers or with `Accept: application/json`,
the endpoint will return JSON `application/json` responses to GET requests.

An example GET request may look like this:

```bash
$ curl --globoff "https://example.com/api/v2/search/terminology/?locale=ar"
```

## Browsable API

When accessed from a browser, Pontoon’s REST API provides a browsable, interactive HTML interface powered by Django REST Framework.

Available at any `/api/v2/` endpoint, the browsable API lets you:

- View and explore JSON data in a human-friendly format
- See validation rules and error messages inline
- Navigate related resources easily via hyperlinks

This interface is especially useful for exploring the API without external tools like Postman or curl.

## Response Customization

You can customize the response by specifying the fields you want to include using the `fields=field_1,field_2,...field_N` query parameter. This allows you to limit the data returned to only the fields you need, reducing payload size and improving performance.

For example, to retrieve only the `name` and `code` fields for `locales`, you can use:

```bash
$ curl --globoff "https://example.com/api/v2/locales/?fields=name,code"
```

This will return a response containing only the specified fields for each locale.

## Pagination

All list-based endpoints are paginated. By default, each page contains up to 100 items.

Use the `?page=N` query parameter to navigate between pages.

An example may look like this:

```bash
$ curl --globoff "https://example.com/api/v2/locales/?page=2"
```

The page size can also be set with the `?page_size=N` query parameter, reaching a maximum of 1000 items.

An example may look like this:

```bash
$ curl --globoff "https://example.com/api/v2/locales/?page_size=50"
```
