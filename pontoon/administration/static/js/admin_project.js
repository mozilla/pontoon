$(function() {

  // Before submitting the form
  $('#admin-form').submit(function (e) {
    // Update locales
    var arr = [];
    $("#selected").parent().siblings('ul').find('li:not(".no-match")').each(function() {
      arr.push($(this).data('id'));
    });
    $('#id_locales').val(arr);

    // Update form action
    var slug = $('#id_slug').val();
    if (slug.length > 0) {
      slug += '/';
    }
    $('#admin-form').attr('action', $('#admin-form').attr('action').split('/projects/')[0] + '/projects/' + slug);
  });

  // Submit form with Enter
  $('html').unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
    if ($('input[type=text]:not("input[type=search]"):focus').length > 0) {
      var key = e.keyCode || e.which;
      if (key === 13) { // Enter
        // A short delay to allow digest of autocomplete before submit
        setTimeout(function() {
          $('#admin-form').submit();
        }, 1);
        return false;
      }
    }
  });

  // Submit form with button
  $('.save').click(function(e) {
    e.preventDefault();
    $('#admin-form').submit();
  });

  // Manually Sync project
  $('.sync').click(function(e) {
    e.preventDefault();

    var button = $(this),
        title = button.html();

    if (button.is('.in-progress')) {
      return;
    }

    button.addClass('in-progress').html('Syncing...');

    $.ajax({
      url: '/admin/projects/' + $('#id_slug').val() + '/sync/'
    }).success(function() {
      button.html('Sync started');
    }).error(function() {
      button.html('Whoops!');
    }).complete(function() {
      setTimeout(function() {
        button.removeClass('in-progress').html(title);
      }, 2000);
    });
  });

  // Suggest slugified name for new projects
  $('#id_name').blur(function() {
    if ($('input[name=pk]').length > 0 || !$('#id_name').val()) {
      return;
    }
    $('#id_slug').attr('placeholder', 'Retrieving...');
    $.ajax({
      url: '/admin/get-slug/',
      data: {
        name: $('#id_name').val()
      },
      success: function(data) {
        var value = (data === "error") ? "" : data;
        $('#id_slug').val(value);
      },
      error: function() {
        $('#id_slug').attr('placeholder', '');
      }
    });
  });

  // Suggest public repository website URL
  $('body').on('blur', '.repo input', function() {
    var val = $(this).val()
      .replace(/\.git$/, '')
      .replace('git@github.com:', 'https://github.com/')
      .replace('ssh://', 'https://');

    $(this).parents('.repository').find('.website-wrapper input').val(val);
  });

  // Delete subpage
  $('body').on('click.pontoon', '.delete-subpage', function (e) {
    e.preventDefault();
    $(this).parent().toggleClass('delete');
    $(this).next().prop('checked', !$(this).next().prop('checked'));
  });
  $('.subpages [checked]').click().prev().click();

  // Add subpage
  var count = $('.subpages:last').data('count');
  $('.add-subpage').click(function(e) {
    e.preventDefault();
    var form = $('.subpages:last').html().replace(/__prefix__/g, count);
    $('.subpages:last').before('<div class="subpages clearfix">' + form + '</div>');
    count++;
    $('#id_subpage_set-TOTAL_FORMS').val(count);
  });

  // Toggle branch input
  function toggleBranchInput(element, value) {
    $(element).parents('.repository').toggleClass('git', $(element).val() === 'git');
  }
  // On select change
  $('body').on('change', '.repository .type-wrapper select', function(e) {
    toggleBranchInput(this);
  });
  // On page load
  $('.repository .type-wrapper select').each(function() {
    toggleBranchInput(this);
  });

  // Add repo
  var $totalForms = $('#id_repositories-TOTAL_FORMS');
  $('.add-repo').click(function(e) {
    e.preventDefault();
    var count = parseInt($totalForms.val(), 10);

    var $emptyForm = $('.repository-empty');
    var form = $emptyForm.html().replace(/__prefix__/g, count);
    $('.repository:last').after('<div class="repository clearfix">' + form + '</div>');

    toggleBranchInput($('.repository:last').find('.type-wrapper select'));

    $totalForms.val(count + 1);
  });
});
