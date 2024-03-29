- Feature Name: Messaging Center
- Created: 2024-03-12
- Associated Issue: 

# Summary

Introduce a Messaging Center feature to make Pontoon the best tool to send communications to localizers directly, allowing sending of targeted in-app notifications and emails within Pontoon itself.

# Motivation

Currently, we can only send in-app notifications with limited targeting capabilities (selected locales within a single product). For any other communications targeting a subset of users we need to rely on engineers to extract email addresses and send emails to the targeted recipients. This feature would allow administrators of a Pontoon instance managing localization projects to send notifications or emails to targeted sets of recipients with more refined criteria such as locales, projects, roles, recency of activity, and level of activity.

# Feature explanation

## Messaging Center

This feature has the ability to compose a message with a subject and body, send a message as an in-app notification and/or email, and target a set of recipients based on commonly used criteria.

### Composing

#### Message Editor

- Top menu item: `Messaging`
  - Item that appears in the top menu only for those with administrator priveleges
  - Navigates to the `Messaging Center` page.
- Title: `Messaging Center`
- Header: `Message type`
  - Selects the type of message to be sent
  - Checkboxes: `Email`, `Notification` (default: both boxes deselected)
  - Validation: Error if no checkbox selected - `You must select at least one message type.`
- Header: `Message editor`
  - Creates a subject and body for emails. Subject line will also be required for in-app notifications, which will have it combined with the body as the first line of the message separated by a newline.
  - Field: `Subject` (text input)
  - Field: `Body` (text input with formatting: markdown or html)
  - Tab: `Preview` - shows a rendered version of the text in `Body` for checking formatting, similar to how the preview for GitHub comments work
  - Validation: 
    - Error if `Subject` field empty: `Your message must include a subject.`
    - Error if `Body` field empty: `Your message must include a body.`

#### Selecting Recipients with Filters

- Header: `Recipients`
  - Select who will receive a message based on a combination of the following filters.
  - `Included User Roles` - enables User Role as a filter.
    - Checkboxes: `Manager`, `Translator`, `Contributor` (multiselect, default: all boxes selected)
    - Validation:
      - Error if `Included User Roles` has no roles selected: `You must select at least one user role.`
  - Subheader: `Filter by Locale`
    - Use existing 2-panel widget like the one already used for selecting locales in Pontoon
    - Choose locales by moving them from `Available` to `Chosen` (all locales available)
    - Include a `Move All` option
    - Validation:
      - Error if no locales selected: `You must select at least one locale.`
  - Subheader: `Filter by Projects`
    - Use a 2-panel widget similar to the one used for selecting locales in Pontoon
    - Choose projects by moving them from `Available` to `Chosen` (all projects available)
    - Include a `Move All` option
    - Validation:
      - Error if no projects selected: `You must select at least one project.`
  - Subheader `Filter by Activity`
    - Button: `Add activity filter`
      - Creates a new section of the form labeled `Activity filter` and an associated button `Remove filter`.
      - Creates a dropdown list `Activity type` associated with this filter
      - `Add activity filter` button persists at the bottom of the form and will still be visible after being clicked, allowing multiple filters to be created
    - Dropdown list: `Activity type`
      - Options: `Select activity type`, `Submitted translations`, `Performed reviews`, `Last login`
      - Select one
      - Default value: `Select activity type`
      - If one or more filters already exist, dynamically remove existing types from the dropdown list
      - Form dynamically displays the appropriate filter inputs below based on the selection in the dropdown. `Select activity type` does not display any filter fields.
      - Validation:
        - Multiple activity filters can be used at the same time
        - Disable `Review message` button and show error message if `Select activity type` selected as a filter in the dropdown: `You must select an activity type when you add an activity filter.`
    - Filter inputs:
      - Inputs for `Submitted translations` / `Performed reviews`
        - `Activity level`
          - Input box: `Minimum` (value required, default value: 0, only accepts non-negative integers)
          - Input box: `Maximum` (value optional, default value: empty, leaving empty will mean there is no maximum and all numbers greater than or equal to the value in `Minimum` will be included.)
          - Tooltip on `Maximum`: `Leave empty to include all numbers greater than or equal to Minimum.`
        - `Timeframe filter`
          - Checkbox (default: deselected): `Enable timeframe filter`
            - Checking the box displays datepickers
          - Datepicker: `From:` (Default value: 1 year before today's date)
          - Datepicker: `To:` (Default value: today's date)
      - Inputs for `Last login`
        - `Timeframe filter`
          - Datepicker: `From:` (Default value: today's date)
          - Datepicker: `To:` (Default value: today's date)

#### Flagging as Transactional

- Header: `Transactional email`
  - By default, emails are sent to users who have enabled opt-in consent. (Does not apply to in-app notifications.)
  - This “Transactional” option flags emails as transactional and sends emails to users regardless of their opt-in status. However, this email content would be restricted to content transactional in nature (e.g. account status notifications, etc.).
  - Checkbox (default: deselected): `This is a transactional email`
  - Text description: `Transactional emails are sent to users who have not opted in to email communication. Transactional emails are restricted in the type of content that can be included.`
  - Validation:
    - Disable `Review message` button and show error message if `Transactional email` enabled but `Message type` does not include `Email`: `You cannnot enable the transactional email option if the Message type does not include email.`

#### Proceed Button
- Button: `Review message`
  - A send button is not displayed on the same page as the message editor and recipient selection to avoid sending an incomplete message or a message to the wrong recipients.
  - When pressed a validation step is performed on inputs to ensure there are no issues with the form. If there are no issues, the user proceeds to the Review/Confirmation page.

### Review

- Title: `Review message`
- A review step is required to reduce errors because messages could be sent to a large number of people. This page allows you to review all aspects of the email before sending, including:
 - A rendered version of the message to ensure things like Markdown tags or html don’t have issues.
 - A summary of who will be receiving the nessage:
    - The number of recipients
    - The filters being applied
  - Whether this is a transactional email. If enabled, a warning will be shown: `Warning: transactional emails are sent to users who have not opted in to email communication. Transactional emails are restricted in the type of content that can be included. When in doubt, please review with legal.`
  - Button: `Send test to myself`
    - Sends the current message to the user creating the message in the same format(s) as it is being sent.
  - Button: `Edit`
    - Clicking the ` Edit` button or navigating back in the browser brings you to the previous page
    - The previously entered content is preserved when `Edit` or the browser's back button is used so work is not lost
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
