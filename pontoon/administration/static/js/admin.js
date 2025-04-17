$(function () {
  console.log('Admin JS loaded');
  $('#toggle-projects').click(function () {
    console.log('Button is clicked');
    const button = $(this);
    const currentShowDisabled = button.data('show-disabled') === true;
    const nextShowDisabled = !currentShowDisabled;

    // Update button text and data attribute
    button.data('show-disabled', nextShowDisabled);
    button.text(
      nextShowDisabled ? 'Enabled projects >' : 'Disabled projects >',
    );

    // Reload the page with the appropriate query param
    const url = new URL(window.location.href);
    url.searchParams.set('show_disabled', nextShowDisabled);
    window.location.href = url.toString();
  });
});
