$(function () {
  const self = Pontoon;

  window.history.replaceState(
    {},
    document.title,
    document.location.href.split('?')[0],
  );

  // Filter notifications
  $('.left-column a').on('click', function () {
    const notifications = $(this).data('notifications');

    // Show all notifications
    if (!notifications) {
      $(
        '.right-column .notification-item, .right-column .horizontal-separator',
      ).show();
      $('.right-column .horizontal-separator').show();

      // Show project notifications
    } else {
      $('.right-column .notification-item').each(function () {
        const isProjectNotification =
          $.inArray($(this).data('id'), notifications) > -1;
        $(this).toggle(isProjectNotification);
        $(this).next('.horizontal-separator').toggle(isProjectNotification);
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

  // Load remaining notifications
  if ($('#server').data('hasMore')) {
    self.NProgressUnbind();

    $.ajax({
      url: '/ajax/notifications/',
      success: function (data) {
        $('#main .notification-list').append(data);

        // Re-apply notification filters
        $('.left-column .selected:not(.all) a').trigger('click');
      },
      error: function () {
        Pontoon.endLoader('Oops, something went wrong.', 'error');
      },
    });

    self.NProgressBind();
  }
});
