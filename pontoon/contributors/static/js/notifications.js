$(function () {
    // Filter notifications
    $('.left-column a').on('click', function () {
        var notifications = $(this).data('notifications');

        // Show all notifications
        if (!notifications) {
            $(
                '.right-column .notification-item, .right-column .horizontal-separator',
            ).show();
            $('.right-column .horizontal-separator').show();

            // Show project notifications
        } else {
            $('.right-column .notification-item').each(function () {
                var isProjectNotification =
                    $.inArray($(this).data('id'), notifications) > -1;
                $(this).toggle(isProjectNotification);
                $(this)
                    .next('.horizontal-separator')
                    .toggle(isProjectNotification);
            });

            $('.right-column .notification-item:visible:last')
                .next('.horizontal-separator')
                .hide();
        }
    });

    // Mark all notifications as read
    if ($('.right-column li.notification-item[data-unread="true"]').length) {
        setTimeout(function () {
            Pontoon.markAllNotificationsAsRead();
        }, 1000);
    }
});
