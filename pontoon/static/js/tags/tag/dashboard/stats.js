
import {AggregateStats} from 'utils/stats';


export default class TagLocaleStats extends AggregateStats {

    get mostApproved () {
        if (!(this.data.length)) {
            return '';
        }
        let approved = 0;
        let mostTranslations;
        this.data.forEach(locale => {
            if (locale.approved_strings > approved) {
                approved = locale.approved_strings;
                mostTranslations = locale;
            }
        });
        return mostTranslations ? mostTranslations.name : '';
    }

    get mostMissingStrings () {
        if (!(this.data.length)) {
            return '';
        }
        let missing = 0;
        let mostMissing;

        this.data.forEach(locale => {
            let missingStrings = (
                locale.total_strings
                    - locale.approved_strings
                    - locale.fuzzy_strings
                    - locale.translated_strings);

            if (missingStrings > missing) {
                missing = missingStrings
                mostMissing = locale;
            }
        });
        return mostMissing ? mostMissing.name : '';
    }

    get mostSuggestions () {
        if (!(this.data.length)) {
            return '';
        }
        let suggestions = 0;
        let mostSuggestions;
        this.data.forEach(locale => {
            if (locale.translated_strings > suggestions) {
                suggestions = locale.translated_strings;
                mostSuggestions = locale;
            }
        });
        return mostSuggestions ? mostSuggestions.name : '';
    }

    get mostTranslations () {
        if (!(this.data.length)) {
            return '';
        }
        let approved = 0;
        let mostTranslations;
        this.data.forEach(locale => {
            if (locale.approved_strings > approved) {
                approved = locale.approved_strings;
                mostTranslations = locale;
            }
        });
        return mostTranslations ? mostTranslations.name : '';
    }

    get teamCount () {
        return this.data.length;
    }
}
