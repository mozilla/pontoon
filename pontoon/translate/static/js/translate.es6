/**
 * Parent component for the entire translation editor.
 */
var TranslationEditor = React.createClass({
  getInitialState: function() {
    return {
      loaded: false,
      entities: [],
      selectedEntity: {},
    };
  },

  componentDidMount: function() {
    let url = `/project/${this.props.project.slug}/locale/${this.props.locale.code}/entities`;
    $.get(url).then((entities) => {
      this.setState({
        loaded: true,
        entities: entities,
        selectedEntity: {},
      });
    });
  },

  render: function() {
    if (!this.state.loaded) {
      return this.loadingIndicator();
    }

    return (
      <div id="translation-editor">
        <aside id="sidebar">
          <EntityList entities={this.state.entities} project={this.props.project} />
          <div id="drag" draggable="true"></div>
        </aside>
      </div>
    );
  },

  /** Hide iframe if no project URL is specified. */
  iframe: function() {
    if (this.state.project.url) {
      return (
        <div>
          <iframe id="source"></iframe>
          <div id="iframe-cover"></div>
        </div>
      );
    } else {
      return '';
    }
  },

  /** Project loading indicator. */
  loadingIndicator: function() {
    return (
      <div id="project-load">
        <div className="inner">
          <div className="animation">
            <div></div>
            <div></div>
            <div></div>
            <div></div>
            <div></div>
          </div>
          <div className="text">"640K ought to be enough for anybody."</div>
        </div>
      </div>
    );
  }
});


var EntityList = React.createClass({
  render: function() {
    let entities = this.props.entities;
    let listBody = <h3 className="no-match"><div>ఠ_ఠ</div>No results</h3>;

    if (entities.length > 1) {
      let editableEntities = entities.filter(entity => entity.body);
      let uneditableEntities = entities.filter(entity => !entity.body);

      // Only show page mesage if we're showing an iframe.
      let notOnPageMessage = '';
      if (this.props.project.url) {
        notOnPageMessage = <h2 id="not-on-page">Not on the current page</h2>;
      }

      listBody = (
        <div className="wrapper">
          <ul className="editables">
            {editableEntities.map(EntityItem.fromEntity)}
          </ul>
          {notOnPageMessage}
          <ul className="uneditables">
            {uneditableEntities.map(EntityItem.fromEntity)}
          </ul>
        </div>
      );
    }

    return (
      <div id="entitylist">
        <EntitySearch />
        {listBody}
      </div>
    );
  }
});


var EntitySearch = React.createClass({
  render: function() {
    return (
      <div className="search-wrapper clearfix">
        <div className="icon fa fa-search"></div>
        <input id="search" type="search" placeholder="Search" />
        <div id="filter" className="select">
          <div className="button selector all">
            <span className="status fa"></span>
            <span className="title">All</span>
          </div>
          <div className="menu">
            <ul>
              <li className="all"><span className="status fa"></span>All</li>
              <li className="untranslated"><span className="status fa"></span>Untranslated</li>
              <li className="fuzzy"><span className="status fa"></span>Needs work</li>
              <li className="translated"><span className="status fa"></span>Unapproved</li>
              <li className="approved"><span className="status fa"></span>Approved</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }
});


var EntityItem = React.createClass({
  render: function() {
    let entity = this.props.entity;
    let translationString = '';
    if (entity.approved_translation) {
      translationString = entity.approved_translation.string;
    } else if (entity.translations.length > 0) {
      translationString = entity.translations[0].string;
    }

    return (
      <li className={classNames('entity', 'limited', this.getEntityStatus(entity),
                                {editable: !entity.body})}>
        <span className="status fa"></span>
        <p className="string-wrapper">
          <span className="source-string">{entity.marked}</span>
          <span className="translation-string">{translationString}</span>
        </p>
        <span className="arrow fa fa-chevron-right fa-lg"></span>
      </li>
    );
  },

  statics: {
    fromEntity: function(entity) {
      return <EntityItem key={entity.pk} entity={entity} />;
    },
  },

  getEntityStatus: function (entity) {
    if (entity.approved_translation) {
      return 'approved';
    } else if (entity.translations.some((t) => t.fuzzy)) {
      return 'fuzzy'
    } else if (entity.translations.length > 0) {
      return 'translated';
    } else {
      return '';
    }
  }
});


var EntityEditor = React.createClass({
  render: function() {
    let entity = this.props.entity;
    return (
      <div id="editor">
        <div id="drag-1" draggable="true"></div>

        <div id="topbar" className="clearfix">
          <a id="back" href="#back"><span className="fa fa-chevron-left fa-lg"></span>Back to list</a>
          <a id="next" href="#next"><span className="fa fa-chevron-down fa-lg"></span>Next</a>
          <a id="previous" href="#previous"><span className="fa fa-chevron-up fa-lg"></span>Previous</a>
        </div>

        <div id="source-pane">
            {this.metadata()}
            <p id="original">{entity.marked}</p>
        </div>

        <textarea id="translation"
                  placeholder="Enter translation"
                  defaultValue={entity.translation[0].string}>
        </textarea>

        <menu>
          <div id="translation-length">
            {entity.translation[0].string.length} / {entity.original.length}
          </div>
          <button id="copy">Copy</button>
          <button id="clear">Clear</button>
          <button id="cancel">Cancel</button>
          <button id="save">Save</button>
        </menu>

        <EditorHelpers entity={entity} />
      </div>
    );
  },

  metadata: function() {
    let metadata = [];
    let entity = this.props.entity;

    if (entity.comment) {
      metadata.push(<span id="comment">{entity.comment}</span>);
    }

    if (entity.source || entity.path || entity.key) {
      metadata.push(<a href="#" className="details">More details</a>);
    }

    if (entity.source) {
      if (typeof(entity.source) === 'object') {
        for (let source of entity.source) {
          metadata.push(<span>#: {source.join(':')}</span>);
        }
      } else {
        metadata.push(<span>{entity.source}</span>);
      }
    }

    if (entity.path) {
      metadata.push(<span>{entity.path}</span>);
    }

    if (entity.key) {
      metadata.push(<span>Key: {entity.key}</span>);
    }

    return (
      <p id="metadata">
        {metadata}
      </p>
    );
  }
});


var EditorHelpers = React.createClass({
  render: function() {
    let entity = this.props.entity;

    return (
      <div id="helpers">
        <nav>
          <ul>
            <li className="active">
              <a href="#history">
                <span>History<span className="fa fa-cog fa-lg fa-spin"></span></span>
              </a>
            </li>
            <li>
              <a href="#machinery">
                <span>Machinery<span className="fa fa-cog fa-lg fa-spin"></span></span>
              </a>
            </li>
            <li>
              <a href="#other-locales">
                <span>Locales<span className="fa fa-cog fa-lg fa-spin"></span></span>
              </a>
            </li>
            <li>
              <a href="#custom-search">
                <span>Search<span className="fa fa-cog fa-lg fa-spin"></span></span>
              </a>
            </li>
          </ul>
        </nav>

        <EntityHistoryList />
        <MachineryList />
        <OtherLocalesList />
        <MachinerySearch />
      </div>
    )
  }
});


var EntityHistoryList = React.createClass({
  getInitialState: function() {
    return {history: []};
  },

  render: function() {
    let historyItems = [];
    if (this.state.history.length < 1) {
      historyItems.push(
        <li className="disabled"><p>No translations available.</p></li>
      )
    } else {
      historyItems = this.state.history.map(item => (
        <EntityHistoryItem key={item.id} item={item} user={this.props.user}></EntityHistoryItem>
      ));
    }

    return (
      <ul>
        {historyItems}
      </ul>
    );
  }
});


var EntityHistoryItem = React.createClass({
  render: function() {
    return (
      <li data-id={this.props.item.id}
          className={classNames({approved: this.props.item.approved})}
          title="Click to copy">
        <header className={classNames('clearfix', this.headerClass())}>
          <div className="info">
            {this.localizerName()}
            <time className="stress" dateTime={this.props.item.date_iso}>{this.props.item.date}</time>
          </div>
          <menu className="toolbar">
            <button className="approve fa" title={this.approveTitle()}></button>
            <button className="delete fa" title="Delete"></button>
          </menu>
        </header>
        <p className="translation">
          {this.props.item.translation}
        </p>
      </li>
    );
  },

  headerClass: function() {
    if (this.props.user.localizer) {
      return 'localizer';
    } else if (this.props.user.email == this.props.item.email &&
               !this.props.item.approved) {
      return 'own'
    } else {
      return '';
    }
  },

  localizerName: function() {
    if (this.props.item.email) {
      let href = 'contributors/' + this.props.item.email;
      return <a href={href}>{this.props.item.user}</a>;
    } else {
      return this.props.item.user;
    }
  },

  approveTitle: function() {
    if (!this.props.item.approved) {
      return 'Approve';
    } else if (this.props.item.approved_user) {
      return 'Approved by '+ this.props.item.approved_user;
    } else {
      return '';
    }
  },
});


var MachineryList = React.createClass({
  render: function() {
    return (
      <section id="machinery">

      </section>
    )
  },
});


var OtherLocalesList = React.createClass({
  render: function() {
    return (
      <section id="other-locales">

      </section>
    )
  },
});


var MachinerySearch = React.createClass({
  render: function() {
    return (
      <section id="custom-search">
        <div className="search-wrapper clearfix">
          <div className="icon fa fa-search"></div>
          <div className="icon fa fa-cog fa-spin"></div>
          <input type="search" autocomplete="off" placeholder="Type and press Enter to search" />
        </div>
        <ul></ul>
      </section>
    );
  },
});


/* Main code */
$(function() {
  let $server = $('#server');
  let project = $server.data('project');
  let locale = $server.data('locale');

  let editor = React.render(
    <TranslationEditor project={project} locale={locale} />,
    document.getElementById('translation-editor-container')
  );
});
