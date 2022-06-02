- Feature Name: Team guidelines for new contributors
- Created: 2022-05-31
- Associated Issue: #2305

# Summary

Provide new contributors with guidelines before making their first contribution to a team.

# Motivation

It has been suggested on various occasions and from various sources, including at the localizer workshops, that the onboarding experience for new contributors needs improvements.

Pontoon homepage and tour lead users towards making their first contribution, but don't provide any team-specific information.

On top of that, new users don't get connected with their team, and team managers don't get any explicit information about new contributors joining their teams.

# Feature explanation

## Translate view tooltip

Before users submits their first suggestion to any team, a tooltip appears near the text editor, with the following content:

It looks like you haven't contributed to this locale yet. Be sure to:
- review the <a href="https://mozilla-l10n.github.io/styleguides/locale-code/">style guide</a>
- check out <a href="/locale-code/info">team information</a>
- contact <a href="/locale-code/contributors">team managers</a>

## Notification for team managers

After the user successfully makes their first suggestion to a particular locale, an in-app notification is sent to team managers, informing them about the new user. Example text:

John Smith has made their first contribution to Locale X (locale-code). Please welcome them to the team!

# Mockup

![](0112/mockup.png)
