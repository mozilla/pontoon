# Pontoon Application Programming Interface

Pontoon provides a set of [RESTful](https://developer.mozilla.org/en-US/docs/Glossary/REST) endpoints via the [Django REST Framework](https://www.django-rest-framework.org/), accessible under `/api/v2/`.

## Authentication

Most endpoints are publicly accessible and require no authentication. A few endpoints require an authenticated user.

Requests can be authenticated either with a session cookie or with a Personal Access Token (PAT). Write endpoints accept only a PAT. You can create a PAT from your [user settings](https://pontoon.mozilla.org/settings/) page (see the [User Accounts & Settings](https://github.com/mozilla/pontoon/blob/main/documentation/docs/localizer/users.md#personal-access-tokens) documentation for details).

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

## Write Endpoints

The following endpoints can write data and always require authentication with a Personal
Access Token. Session cookies are not accepted.

### `POST /api/v2/upload/translations/`

Update translations from an uploaded translation file, as the authenticated user. This
is the API equivalent of the **Upload Translations** button in the translate app.

The request body is `multipart/form-data` with these fields:

| Field        | Description                                                 |
| ------------ | ----------------------------------------------------------- |
| `project`    | Project slug                                                |
| `locale`     | Locale code                                                 |
| `resource`   | Resource path within the project                            |
| `uploadfile` | Translation file, in the same format as the target resource |

```bash
$ curl -X POST \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -F "project=firefox" \
  -F "locale=it" \
  -F "resource=browser/browser.ftl" \
  -F "uploadfile=@browser.ftl" \
  "https://example.com/api/v2/upload/translations/"
```

A successful request returns a summary of the import:

```json
{
  "updated": 12,
  "unchanged": 3,
  "undefined_keys": [["obsolete_key"]],
  "undefined_keys_count": 1
}
```

- `updated`: translations added or replaced. Uploaded translations replace the
  current approved translation, or approve a matching suggestion.
- `unchanged`: translations identical to the current approved, pretranslated or fuzzy
  one, ignored.
- `undefined_keys`: keys of translations with no matching string in Pontoon, ignored.
  Each key is a list of strings, in the same format as the `key` field of entities.
  Only the first 100 keys are listed.
- `undefined_keys_count`: total number of keys with no matching string in Pontoon,
  before truncation.

The upload is additive: strings missing from the uploaded file are left untouched, so
partial files can be used to update a subset of translations. Re-uploading an unchanged
file succeeds with `"updated": 0`. A file that cannot be parsed, or that contains no
translations at all, is rejected with `400` rather than reported as an unchanged upload,
so `"updated": 0` always means the file was valid and simply didn't change anything.

Requirements and limits:

- You must have translator rights for the target locale, and the project locale must not
  be read-only. Otherwise the request is rejected with `403`.
- The project must not be disabled, and both the project and the resource must be
  enabled for the target locale. Otherwise the request is rejected with `404`.
- Uploaded files must be under 5000 kB, and must match the format of the target
  resource.
- The endpoint is rate limited per user, with a burst limit of 30 calls per minute and a
  sustained limit of 180 calls per hour by default (configurable via
  `API_UPLOAD_THROTTLE_BURST` and `API_UPLOAD_THROTTLE_SUSTAINED`). The two limits are
  not independent: calls rejected by the burst limit still count against the sustained
  limit, so a client that keeps calling after a `429` spends its hourly quota on
  rejected calls. For example, 30 accepted uploads followed by 150 rejected ones exhaust
  the hourly quota, locking the client out for one hour.

Uploaded translations are written to the database immediately, and pushed to the
project's VCS repository by the next sync.

Status codes:

| Code  | Meaning                                                                                                    |
| ----- | ---------------------------------------------------------------------------------------------------------- |
| `200` | Upload accepted (possibly with `"updated": 0`)                                                             |
| `400` | Missing or invalid field, unsupported format, unparseable or empty file, or file too large                 |
| `403` | Missing token, invalid or expired token, or insufficient permission                                        |
| `404` | Unknown or disabled project, unknown locale or resource, or project or resource not enabled for the locale |
| `409` | A concurrent upload changed the same translations; retry the request                                       |
| `429` | Rate limit exceeded                                                                                        |
