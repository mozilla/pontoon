

export class Stats {

    /* Takes basic stats values as provided by Django
     * and turns them into stats as required to build
     * a stats progress chart or other stats summary
     *
     */

    constructor (data) {
        this.data = data;
    }

    get approvedPercent() {
        if (this.translatedStrings === 0 || this.totalStrings === 0) {
            return 0;
        }
        return parseInt(
            Math.floor(
                this.translatedStrings
                    / parseFloat(this.totalStrings) * 100));
    }

    get fuzzyShare () {
        return this._share(this.fuzzyStrings);
    }

    get fuzzyStrings () {
        return this.data ? this.data.fuzzy_strings || 0 : 0;
    }

    get missingShare () {
        if (this.totalStrings === 0) {
            return 0;
        }
        return this._share(this.missingStrings);
    }

    get missingStrings () {
        return (
            this.totalStrings
                - this.translatedStrings
                - this.fuzzyStrings
                - this.suggestedStrings);
    }

    get suggestedShare () {
        return this._share(this.suggestedStrings);
    }

    get suggestedStrings () {
        return this.data && this.data.translated_strings || 0 ? this.data.translated_strings : 0;
    }

    get totalStrings () {
        return this.data && this.data.total_strings || 0 ? this.data.total_strings : 0;
    }

    get translatedShare () {
        return this._share(this.translatedStrings);
    }

    get translatedStrings () {
        return this.data && this.data.approved_strings ? this.data.approved_strings : 0;
    }

    _share (item) {
        if (item === 0 || this.totalStrings === 0) {
            return 0;
        }
        return Math.round(item / parseFloat(this.totalStrings) * 100);
    }
}


export class AggregateStats extends Stats {

    get translatedStrings () {
        if (!this._translated) {
            this._translated = this.data.map(x => x.approved_strings).reduce((_s, x) => _s + x);
        }
        return this._translated;
    }

    get fuzzyStrings () {
        if (!this._fuzzy) {
            this._fuzzy =  this.data.map(x => x.fuzzy_strings).reduce((_s, x) => _s + x);
        }
        return this._fuzzy;
    }

    get suggestedStrings () {
        if (!this._suggested) {
            this._suggested = this.data.map(x => x.translated_strings).reduce((_s, x) => _s + x);
        }
        return this._suggested;
    }

    get totalStrings () {
        if (!this._total) {
            this._total = this.data.map(x => x.total_strings).reduce((_s, x) => _s + x);
        }
        return this._total;
    }
}
