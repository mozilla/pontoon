- Feature Name: Pretranslated status
- Created: 2020-09-21
- Associated Bug: https://bugzilla.mozilla.org/show_bug.cgi?id=1666320

# Summary

Introduce a new translation status for Pretranslated strings to differentiate them from Fuzzy strings.

# Motivation

Pretranslation is the process of using machines to translate content before it's translated by human translators. If pretranslation is enabled for the project, any newly added source string gets pretranslated using translation memory (if 100% match is found) or machine translation.

Pretranslations are assigned translation status Fuzzy, which allows us to:
1. Immediately send them to version control system.
2. Make them available in the product.
3. Inform localizers that these strings should be given another look.
4. Run quality checks on them to identify any errors or warnings.

The caveat however is that translation status Fuzzy is also used for [fuzzy](https://www.gnu.org/software/gettext/manual/html_node/Fuzzy-Entries.html) translations of the Gettext system (filenames ending in .po), which are **not** used in the product. That means bullet point #2 isn't valid for projects using the Gettext system - pretranslated strings in .po files will not make it to the product unless human translator approves them.

We need to make pretranslation work according to all 4 items from the list above, consistently across all file formats (including .po).

# Feature explanation

The obvious solution is to introduce a new "Pretranslated" translation status to differentiate pretranslated strings from Fuzzy. However, while it solves the problem, adding a new translation status also adds more data to the already condensed dashboards and increases complexity.

So instead, we make the following two steps:
1. Treat Gettext Fuzzy strings as Missing.
2. Replace Fuzzy status with Pretranslated.

Let's have a closer look at each of them.

# Treat Gettext Fuzzy strings as Missing

We treat Gettext Fuzzy strings as Missing instead of Pretranslated on dashboards, in string list, in progress chart, i.e. everywhere.

Internally, we keep using the fuzzy=True flag for Fuzzy strings, which allows us to distinct them from Missing and:
1. Sync them with version control system.
2. Run quality checks on them.
3. Set fuzzy flag accordingly in the .po file.

Not showing Fuzzy strings on dashboards makes even more sense considering that only 1,180 out of 85,995 (< 1.4%) localizable resources currently enabled on [pontoon.mozlla.org](https://pontoon.mozilla.org/) use .po format.

Fuzzy filter is moved from Status filters to Extra filters. Visual representation of Fuzzy strings in the History panel remains unchanged (yellow icon).

# Replace Fuzzy status with Pretranslated

We rename Fuzzy status to Pretranslated (in both, the UI and the code). In addition to that, we should also consider changing the shade of yellow (used to represent Fuzzy strings) slightly towards green.
