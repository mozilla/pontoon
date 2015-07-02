import {Project} from './models.js';
import TranslateView from './TranslateView.js';


/* Main code */
$(function() {
  let $server = $('#server');
  let project = new Project($server.data('project'));
  let locale = $server.data('locale');
  let csrfToken = $server.data('csrf');

  $.ajaxSetup({
    headers: {'X-CSRFToken': csrfToken}
  });

  let editor = React.render(
    <TranslateView currentProject={project} locale={locale} />,
    document.getElementById('translation-view-container')
  );

  // Event handlers outside of the main React tree.
  let $doc = $(document.documentElement);

  // Toggle the sidebar.
  $doc.on('click', '#switch', (e) => {
    e.preventDefault();

    let $menuButton = $(e.target);
    $menuButton.toggleClass('opened');
    editor.toggleSidebar();
  });
});
