import {NotificationList} from './TranslateView.js';


export let notify = {
    basic(message, tags) {
        NotificationList._singleton.addNotification(message, tags);
    },

    error(message) {
        this.basic(message, ['error']);
    },

    success(message) {
        this.basic(message, ['success']);
    }
};
