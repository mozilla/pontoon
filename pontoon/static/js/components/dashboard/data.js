
import {DataManager} from 'utils/data';
import {Stats} from 'utils/stats';


export class DashboardDataManager extends DataManager {
    /*
     * Normalizes dashboard data for use in Dashboard widgets
     */

    constructor (component, data) {
        super(component, data);
        this.component = component;
        this._stats;
    }

    get statData () {
        return {}
    }

    get stats () {
        if (!this._stats) {
            this._stats = new this.statsClass(this.statData);
        }
        return this._stats;
    }

    get components () {
        return this.component.props.components || {};
    }

    get statsClass () {
        return Stats;
    }

    get summaryInfo () {
        return {
            'Number of teams': this.stats.teamCount,
            'Most translations': this.stats.mostTranslations,
            'Most suggestions': this.stats.mostSuggestions,
            'Most missing strings': this.stats.mostMissingStrings,
            'Most enabled strings': this.stats.mostApproved};
    }

    get summaryStats () {
        return {
            translated: {label: 'Translated strings', value: this.stats.translatedStrings},
            suggested: {label: 'Suggested strings', value: this.stats.suggestedStrings},
            fuzzy: {label: 'Fuzzy strings', value: this.stats.fuzzyStrings},
            missing: {label: 'Missing strings', value: this.stats.missingStrings},
            all: {label: 'All strings', value: this.stats.totalStrings}};
    }

    get tabs () {
        return this.data.dashboard.tabs;
    }

    get toolbar () {
        return this.data.dashboard.toolbar;
    }

    get title () {
        return this.data.dashboard.context.title;
    }

    get subtitle () {
        return this.data.dashboard.context.subtitle;
    }
}
