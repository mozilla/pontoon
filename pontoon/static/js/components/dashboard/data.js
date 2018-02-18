
import {DataManager} from 'utils/data';
import {Stats} from 'utils/stats';


export class DashboardDataManager extends DataManager {
    /*
     * Normalizes dashboard data for use in Dashboard widgets
     */

    constructor (state) {
        super(state);
        if (!this.statsClass) {
            this.statsClass = Stats;
        }
        if (!this.statData) {
            this.statData = {};
        }
    }

    get stats () {
        return this._stats = !this._stats ? new this.statsClass(this.statData): this._stats;
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
