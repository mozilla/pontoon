
export default class Datetime {

    constructor (datetime, locale) {
        this.datetime = new Date(datetime);
        this.locale = locale || 'en-GB';
    }

    get date () {
        return new Intl.DateTimeFormat(
            this.locale, this.dateFormat).format(this.datetime);
    }

    get dateFormat () {
        return {
            day: 'numeric',
            month: 'long',
            year: 'numeric'}
    }

    get time () {
        return new Intl.DateTimeFormat(
            this.locale, this.timeFormat).format(this.datetime);
    }

    get timeFormat () {
        return {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'}
    }
}
