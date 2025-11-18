# Pontoon Application Programming Interface

Pontoon provides a set of [RESTful](https://developer.mozilla.org/en-US/docs/Glossary/REST) endpoints via the [Django REST Framework](https://www.django-rest-framework.org/), accessible under `/api/v2/`.

> 🔐 Added on September 2, 2025 at 12:37 UTC: The REST API is in beta. While stable for general use, its structure may change as we continue development.

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
