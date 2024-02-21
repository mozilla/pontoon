- Feature Name: Email consent opt-in and Unsubscribe page
- Created: 2024-02-21
- Associated Issue: #3109

# Summary

Work required to enable email communication with Pontoon users: opt-in consent user settings, methods for collecting user opt-in, and an unsubscribe page via a single page without logging in.

# Motivation

There does not exist currently an email communication consent opt-in for users who register with Pontoon. This restricts our ability to reach contributors outside of the platform and reduces our effectiveness in keeping localizers informed and engaged. So we need to create settings that allow users to control their ability to opt in to email messages.

This will allow us to reach out within legal compliance to the wider audience of registered users for things such as surveys, online events, etc. Future major platform enhancements will be able to build off this work, and starting this early will provide enough time to ensure interested and active contributors are opted-in ahead of time.

Value for users / problems solved:
- Users can select their preference for email communication
- Engagement/reach expanded beyond logged-in active Pontoon users


# Feature explanation

## Email communication user settings

The email opt-in consent option is available under an “Email communications” option in user preferences. “Contact email address” should be moved from Personal information to under this section and an option for non-transactional mass emails opt-ing should be added.

These user email communication preferences are stored and referenced in database to determine if emails should be sent to the user.


(Section: content)
- Section title: “Email communications”
- Input field: Contact email address
- Subtitle of input: “If provided, this email address will be used for email communications and will appear under your Profile page instead of the email used for login.”
- Check box: “Receive updates related to localization at Mozilla, projects on Pontoon, and updates to the Pontoon platform.”
- Consent: “I’m okay with Mozilla handling my personal information as explained in this <a href="https://www.mozilla.org/en-US/privacy/websites/">Privacy Notice</a>."

## Standalone page for email consent shown after existing user log-in

We need to make existing users aware of the new email communication preference.

Upon login (after a user’s previous session expires) an email consent page should be displayed to existing users logging in for the first time after the consent feature is enabled. 

They should be shown two buttons, one to opt-in to emails or one declining to opt-in. This should not be shown again if the user clicks either of the buttons, but should be shown again upon next login if the user closed their tab/browser.

This page also should not be shown if the user has opted-in via their settings.

(Section: content)
- Header: "Update your email communication preferences"
- Sub-header: "You can now choose your email communication preferences within Pontoon."
- Body: "Would you like to receive updates related to localization at Mozilla, projects on Pontoon, and updates to the Pontoon platform by email?”
- Consent: “By enabling email updates, I’m okay with Mozilla handling my personal information as explained in this <a href="https://www.mozilla.org/en-US/privacy/websites/">Privacy Notice</a>."
- Button: "Enable email updates”
- Button: "No, thank you"
- Body: “You can update your email communication preferences at any time in your settings."

## New account creation email opt-in

Ideally, we would like users to set up their email communication preferences right away upon successful account creation.

After a user successfully creates their Pontoon account, display a standalone page which redirects to the homepage after the user enables or rejects email updates. This page informs the user of successful account creation and request for updating email communication preferences.

They should be shown two buttons, one to opt-in to emails or one declining to opt-in. This should not be shown again if the user clicks either of the buttons, but the standalone page for email consent (above) should be shown again upon next login if the user closed their tab/browser.

(Section: content)
- Header: "Welcome to Pontoon!"
- Sub-header: "You have successfully created your Pontoon account."
- Body: "Would you like to receive updates related to localization at Mozilla, projects on Pontoon, and updates to the Pontoon platform? This can be changed at any time in your settings."
- Button: "Enable email updates”
- Button: "No, thank you"
- Consent: “By enabling email updates, I’m okay with Mozilla handling my personal information as explained in this <a href="https://www.mozilla.org/en-US/privacy/websites/">Privacy Notice</a>."

## Additional card for tour

As part of new user onboarding, point new users to user preferences and call out the ability to enable email communication preferences.

(Section: content)
- Header: Stay up to date
- Body: "You can receive updates related to localization at Mozilla, projects on Pontoon, and updates to the Pontoon platform by email. If you'd like to stay up to date, you can enable these emails in your settings."

*Display if user logged in:*
- Button: "Enable email updates"
- Consent: “By enabling email updates, I’m okay with Mozilla handling my personal information as explained in this <a href="https://www.mozilla.org/en-US/privacy/websites/">Privacy Notice</a>."

## Unsubscribe page

Legal regulations (e.g. CAN-SPAM act) have specific requirements to include an unsubscribe link in commercial email messages to manage email preferences without requiring a log-in.

As a user I can:
- Access my unique/personal unsubscribe page through a link without logging in. The link would typically be included with non-transactional emails from Pontoon as an “Unsubscribe” link in the footer.
  - Link technical specs:
  1) Pontoon generates a random unique identifier and assigns it to each user. The algorithm doesn't use any existing user data to generate the ID, which needs to be sufficiently complex to avoid a potential attacker guessing.
  2) The unsubscribe page can be accessed without login. If a user ID is not provided, or it's incorrect, it will display an error message.
  3) Unsubscribe links in emails will include the user's unique identifier in the URL to correctly identify the user.
- All options are managed from a single page; I do not need to navigate from the page linked in the email to manage subscriptions.
- Unsubscribe from all emails with a single button.
- Subscribe for emails with a single button
- Receive a confirmation that I have successfully unsubscribed/subscribed. I am also instructed how to change my subscriptions later through my user preferences.
- (In future implementations) Select specific categories of emails to receive / no longer receive. 
