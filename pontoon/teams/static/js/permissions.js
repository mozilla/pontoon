$(function () {
  const container = $('#main .container');

  function inputHidden(name, value, cssClass) {
    return $(
      '<input class="' +
        (cssClass || '') +
        '" type="hidden" name="' +
        name +
        '" value="' +
        value +
        '">',
    );
  }

  container.on('click', '#permissions-form .save', function (e) {
    e.preventDefault();
    const $form = $('#permissions-form');

    // Remove stale permissions items (bug 1416890)
    $('input.permissions-form-item').remove();

    // Before submitting the form, update translators and managers
    $.each(['translators', 'managers'], function (i, value) {
      const data = $form.find('.user.' + value + ' li');
      data.each(function () {
        const itemId = $(this).data('id');

        if ($(this).parents('.general').length > 0) {
          $form.append(
            inputHidden('general-' + value, itemId, 'permissions-form-item'),
          );
        } else {
          // We have to retrieve an index of parent project locale form
          const localeProjectIndex = $(this)
            .parents('.project-locale')
            .data('index');
          $form.append(
            inputHidden(
              'project-locale-' + localeProjectIndex + '-translators',
              itemId,
              'permissions-form-item',
            ),
          );
        }
      });
    });

    const $tooltip = $('#badge-tooltip-container');

    $.ajax({
      url: $('#permissions-form').prop('action'),
      type: $('#permissions-form').prop('method'),
      data: $('#permissions-form').serialize(),
      success: function (response) {
        Pontoon.endLoader('Permissions saved.');
        const badgeLevel = $(response).find('#community-builder-level').val();

        // Check for new badge notification
        if (badgeLevel > 0) {
          $tooltip.show();

          // Handle discard
          $(document).on('click', function (e) {
            if (!$tooltip.is(e.target) && $tooltip.has(e.target).length === 0) {
              $tooltip.hide();
            }
          });

          // Force a re-render of the text with the proper badge level
          $tooltip
            .find('.badge-tooltip-info')
            .text(`Community Builder Badge level gained: Level ${badgeLevel}`);

          const duration = 2000;
          const animationEnd = Date.now() + duration;
          const defaults = {
            startVelocity: 30,
            spread: 360,
            ticks: 60,
            zIndex: 0,
          };

          function randomInRange(min, max) {
            return Math.random() * (max - min) + min;
          }

          const interval = setInterval(function () {
            const timeLeft = animationEnd - Date.now();

            if (timeLeft <= 0) {
              return clearInterval(interval);
            }

            const particleCount = 50 * (timeLeft / duration);
            // since particles fall down, start a bit higher than random
            confetti({
              ...defaults,
              particleCount,
              origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
            });
            confetti({
              ...defaults,
              particleCount,
              origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
            });
          }, 250);
        }
      },
      error: function () {
        Pontoon.endLoader('Oops, something went wrong.', 'error');
      },
    });

    $tooltip.find('button').one('click', function (e) {
      e.preventDefault();
      $tooltip.hide();
    });
  });

  // Switch available users
  container.on('click', '.user.available label a', function (e) {
    e.preventDefault();

    $(this).addClass('active').siblings('a').removeClass('active');

    const available = $(this).parents('.user.available');
    available.find('li').show();

    if ($(this).is('.contributors')) {
      available.find('li:not(".contributor")').hide();
    }

    available.find('.search-wrapper input').trigger('input').focus();
  });

  // While in contributors tab, search contributors only
  // Has to be attached to body, like the input.search event in main.js
  $('body').on(
    'input.search',
    '.user.available .menu input[type=search]',
    function () {
      const available = $(this).parents('.user.available');

      if (available.find('label a.contributors').is('.active')) {
        available.find('li:not(".contributor")').hide();
      }
    },
  );

  // Focus project selector search field
  container.on('click', '#project-selector .selector', function () {
    $('#project-selector .search-wrapper input').focus();
  });

  // Add project
  container.on('click', '#project-selector .menu li', function () {
    const slug = $(this).data('slug'),
      $permsForm = $(".project-locale[data-slug='" + slug + "']");

    $('.project-locale:last').after($permsForm.removeClass('hidden'));

    $permsForm.append(
      inputHidden(
        'project-locale-' +
          $permsForm.data('index') +
          '-has_custom_translators',
        1,
      ),
    );

    // Update menu (must be above Copying Translators)
    $(this).addClass('hidden').removeClass('limited').removeAttr('style');
    if ($('#project-selector .menu li:not(".hidden")').length === 0) {
      $('#project-selector').addClass('hidden');
    }

    // Initialize Project Contributors (must be above Copying Translators)
    if ($permsForm.find('.user.available li').length === 0) {
      $('.permissions-groups.general .user li').each(function () {
        $(this)
          .clone()
          .appendTo(
            ".project-locale[data-slug='" + slug + "'] .user.available ul",
          );
      });
    }

    // Initialize Project Translators with Managers and Translators from the General section
    $('.permissions-groups.general .user:not(".available") li').each(
      function () {
        $permsForm
          .find('.user.available li[data-id="' + $(this).data('id') + '"]')
          .click();
      },
    );

    // Scroll to the right project locale
    $('html, body').animate(
      {
        scrollTop: $permsForm.offset().top,
      },
      500,
    );
  });

  // Remove project
  container.on('click', '.remove-project', function (e) {
    const $permsForm = $(this).parents('.project-locale');
    e.preventDefault();

    $('#project-selector').removeClass('hidden');
    $("#project-selector li[data-slug='" + $permsForm.data('slug') + "']")
      .removeClass('hidden')
      .addClass('limited');

    $permsForm.find('input[name$=has_custom_translators]').remove();

    $permsForm.addClass('hidden');
    $permsForm.find('.select.translators li').each(function () {
      $permsForm.find('.select.available ul').append($(this).remove());
    });
  });
});
