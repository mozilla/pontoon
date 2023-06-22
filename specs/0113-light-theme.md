- Feature Name: Light theme
- Created: 2023-06-22
- Associated Issue: #2141

# Summary

Implement light theme and enable users to switch between the (current) dark theme and the light theme.

# Motivation

Over the years, many users have expressed preference for a light color theme over the Pontoon default dark theme. Having the ability to switch themes will also allow us to implement high contrast themes, which benefit low vision users, increase readability and reduce website’s visual noise.

# Implementation notes

In the first step, we'll replace existing hardcoded color values with CSS variables. We'll store those in separate CSS files, with one version of each file for each theme. Users will be able to switch theme in their settings.

See below for the actual light theme color values.

# Color pairs

TODO

# Mockup

![](0113/translate.png)
![](0113/dashboard.png)
