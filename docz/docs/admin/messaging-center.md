# Messaging Center

The Messaging Center allows Administrators to send targeted emails and in-app notifications to contributors, with advanced filtering options.

## Accessing the Messaging Center

Click **Messaging** in the page header when logged in as an Administrator. The Messaging Center is at `/messaging/`.

## Composing a message

### Message type

At the top of the page, choose one or more delivery types:

| Type | Notes |
|---|---|
| **Notification** | Sent as an in-app notification. Not included in notification email digests. |
| **Email** | Sent as an email. By default, only sent to users who have opted in to *News and updates*. |
| **Both** | Sends both a notification and an email. |

For emails, if the message is **transactional** (e.g., about an account action), check the **Transactional** option. Transactional emails are sent even to users who have not opted in to email communication.

### Subject and body

Enter your message using the **Subject** and **Body** fields.

## Audience filtering

### By role

Select whether to send to **Managers**, **Translators**, **Contributors**, or **All of them**.

### By locale

All locales are included by default (shown in the **Chosen** column). Remove individual locales by clicking them to move them to the **Available** column. Use **MOVE ALL** to move all locales at once between columns.

### By project

All projects are included by default. Remove individual projects by clicking them. Use **MOVE ALL** to move all projects.

### By activity

Filter recipients based on their contribution history:

- **Number of translations submitted** — minimum or maximum threshold.
- **When they last submitted a translation** — date range.

## Sending

After configuring the message and audience, click **Send** to deliver. Recipients are determined by the intersection of all applied filters.

!!! note
    Notifications sent via the Messaging Center are **not** included in the regular notification email digests that users receive.
