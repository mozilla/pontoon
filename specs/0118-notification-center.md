- Feature Name: Notification Center
- Created: 2024-03-12
- Associated Issue: 

# Summary

Introduce a Notification Center feature to make Pontoon the best tool to send communications to localizers directly, allowing sending of targeted in-app notifications and emails within Pontoon itself.

# Motivation

Currently, we can only send in-app notifications with limited targeting capabilities (selected locales within a single product). For any other communications targeting a subset of users we need to rely on engineers to extract email addresses and send emails to the targeted recipients. This feature would allow administrators of a Pontoon instance managing localization projects to send notifications or emails to targeted sets of recipients with more refined criteria such as locales, projects, roles, recency of activity, and level of activity.

# Feature explanation

## Notification Center

This feature has the ability to compose a message with a subject and body, send a message as either an in-app notification or email, and target a set of recipients based on commonly used criteria.

### Required functionality:

- Title: `Notification Center`
- Header: `Message type`
  - Selects the type of message to be sent
  - Checkboxes: `Email`, `Notification` (multiselect, default: both boxes empty)
  - Validation: Error if no checkbox selected - `You must select at least one message type.`
- Header: `Message editor`
  - Creates a subject and body for emails. Subject line will be required for in-app messages; in app-messages have the subject line combined with the body message as the first line of the message separated by a newline.
  - Field: `Subject` (text input)
  - Field: `Body` (text input with formatting: markdown or html)
  - Button: `Preview` - shows a rendered version of the text in `Body` for checking formatting, similar to how the preview for GitHub comments work
  - Validation: 
    - Error if `Subject` field empty: `Your message must include a subject.`
    - Error if `Body` field empty: `Your message must include a body.`
- Header: `Recipients`
  - Select who will receive a message based on a combination of the below filters.
  - Checkbox: `Filter by User Role` (default empty) - enables User Role as a filter.
    - Checkboxes: `Manager`, `Translator`, `Contributor` (multiselect, default: all boxes empty)
    - Validation:
      - Error if `Filter by User Role` enabled but no roles selected: `You must select at least one user role.`
  - Checkbox: `Filter by Locale` (default empty) - enables Locale as a filter.
    - Use existing 2-panel widget already used for selecting locales in Pontoon
    - Choose locales by moving them from `Available` to `Chosen`(all locales available)
    - Include a `Move All` option
    - Validation:
      - Error if `Filter by Locale` enabled but no locales selected: `You must select at least one locale.`
  - Checkbox: `Projects`
    - Use existing 2-panel widget already used for selecting locales in Pontoon
    - Choose projects by moving them from `Available` to `Chosen` (all projects available)
    - Include a `Move All` option
  - Subheader `Filter by Activity`
    - Button: `Add activity filter`
      - Creates a new section of the form labeled `Activity filter` and an associated button `Remove filter`.
      - Creates a dropdown list `Activity type` associated with this filter
      - `Add activity filter` button persists at the bottom of the form and will still be visible after being clicked, allowing multiple filters to be created
    - Dropdown list: `Activity type`
      - Options: `Select activity type`, `Submitted translations`, `Performed reviews`, `Last login`
      - Select one
      - Default value: `Select activity type`
      - Form dynamically displays the appropriate filter inputs below based on the selection in the dropdown. `Select activity type` does not display any filter fields.
      - Validation:
        - Multiple activity filters can used at the same time
        - Error if more than one filter of the same type used: `You cannot use multiple of the same activity type.`
        - Error if `Select activity type` selected as a filter in the dropdown: `You must select an activity type when you add an activity filter.`
    - Filter inputs:
      - Inputs for `Submitted translations` / `Performed reviews`
        - `Activity level`
          - Input box: `Minimum`  (value required, default value: 0, only accepts non-negative integers)
          - Input box: `Maximum` (value optional, default value: empty, leaving empty will mean there is no maximum and all numbers greater than or equal to the value in `Minimum` will be included.
          - Tooltip on `Maximum`: `Leave empty to include all numbers greater than or equal to Minimum.`
        - `Timeframe filter`
          - Checkbox (default empty): `Enable timeframe filter`
            - Checking the box displays datepickers
          - Datepicker: `From:` (Default value: today's date)
          - Datepicker: `To:` (Default value: today's date)
      - Inputs for `Last login`
        - `Timeframe filter`
          - Datepicker: `From:` (Default value: today's date)
          - Datepicker: `To:` (Default value: today's date)
- Header: `Transactional email`
  - By default, emails are sent to users who have enabled opt-in consent. (Does not apply to in-app notifications.)
  - This “Transactional” option flags emails as transactional and sends emails to users regardless of their opt-in status. However, this email content would be restricted to content transactional in nature (e.g. account status notifications, etc.).
  - Checkbox (default empty): `This is a transactional email`
  - Text description: `Transactional emails are sent to users who have not opted in to email communication. Transactional emails are restricted in the type of content that can be included.`
  - Validation:
    - Error if `Transactional email` enabled but `Message type` does not include `Email`: `You cannnot enable the transactional email option if the Message type does not include email.`
- Button: `Review message`
  - A send button is not displayed on the same page as the message editor and recipient selection to avoid sending an incomplete message or a message to the wrong recipients.
  - When pressed a validation step is performed on inputs to ensure there are no issues with the form. If there are no issues, the user proceeds to the Review/Confirmation page.

- Title: `Review message`
- A review step is required to reduce errors because messages could be sent to a large number of people. This page allows you to review all aspects of the email before sending, including:
 - A rendered version of the message to ensure things like Markdown tags or html don’t have issues.
 - A summary of who will be receiving the nessage:
    - The number of recipients
    - The filters being applied
  - Whether this is a transactional email. If enabled, a warning will be shown: `Warning: transactional emails are sent to users who have not opted in to email communication. Transactional emails are restricted in the type of content that can be included. When in doubt, please review with legal.`
  - Button: `Edit`
    - Clicking the `Edit` button or navigating back in the browser brings you to the previous page
    - The previously entered content is preserved when `Edit` or the browser's back button is useds so work is not lost
  - Checkbox (default empty): `I’ve reviewed the work and this is ready to be sent.`
    - This is another safeguard to avoid accidentally sending messages without thorough review.
    - Validation:
      - Error if this is not checked: `You must confirm that you have reviewed the contents of this message.`
  - Button: `Send`
    - Triggers validation step
    - Initiates the sending of the email and/or notification

## Email Content

When sending an email to users via the Notification Center, emails include the following content:
- Subject: Content filled from “Subject” field in Notification Center
- Body: Content filled from “Body” field in Notification Center (rendered in email compliant HTML)
- Footer: Added to the bottom of all non-transactional emails: `You’re receiving this email as a contributor to Mozilla localization on Pontoon. <br>To no longer receive emails like these, unsubscribe here: <unsubscribe-link>Unsubscribe</unsubscribe-link>.`

## Other

- Emails should only be sent to opted-in users by default.
  - In-app notifications do not require opt-in consent.
  - Flagging an email as “Transactional” will ignore this restriction.
