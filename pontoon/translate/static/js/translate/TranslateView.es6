import {Entity, Project} from './models.js';
import TranslationEditor from './TranslationEditor.js';
import TranslationSelector from './TranslationSelector.js';

let CSSTransitionGroup = React.addons.CSSTransitionGroup;


export default class TranslateView extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      loaded: false,
      entities: [],
      projects: [],
    };
  }

  componentDidMount() {
    $.when(
      Entity.fetchAll(this.props.currentProject.slug, this.props.locale.code),
      Project.fetchAll()
    ).then((entities, projects) => {
      this.setState({
        loaded: true,
        entities: entities,
        projects: projects
      });
    });
  }

  render() {
    let editor = null;
    if (this.state.loaded) {
      editor = <TranslationEditor project={this.props.currentProject}
                                  locale={this.props.locale}
                                  entities={this.state.entities}
                                  onSaveTranslation={this.saveTranslation.bind(this)} />
    } else {
      editor = <LoadingScreen />;
    }

    return (
      <div className="translation-view">
        <header className="header">
          <TranslationSelector currentProject={this.props.currentProject}
                               projects={this.state.projects} />
          <NotificationList />
        </header>
        {editor}
      </div>
    );
  }

  saveTranslation(entity, string) {
    entity.updateTranslation(string, this.props.locale.code).then((newEntity) => {
      notify.success('Translation updated.');
      this.setState((state, props) => {
        let index = state.entities.findIndex((e) => e.pk === entity.pk);
        state.entities[index] = newEntity;
        return {entities: state.entities}
      })
    }).fail(() => {
      notify.error('Error occurred while updating translation, please try again.');
    });
  }
}


class LoadingScreen extends React.Component {
  render() {
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
}


export class NotificationList extends React.Component {
  constructor(props) {
    super(props);

    NotificationList._singleton = this;
    this.state = {
      notifications: []
    };
  }

  render() {
    let messages = [];
    for (let k = 0; k < this.state.notifications.length; k++) {
      let notification = this.state.notifications[k];

      messages.push(
        <li key={`${notification.id}`}
            className={classNames('message', ...notification.tags)}
            onClick={this.closeNotification.bind(this, k)}>
          {notification.message}
        </li>
      )
    }

    return (
      <CSSTransitionGroup transitionName="notification"
                          component="ul"
                          className="notifications">
          {messages}
      </CSSTransitionGroup>
    )
  }

  closeNotification(index) {
    this.setState((state, props) => {
      state.notifications.splice(index, 1);
      return {notifications: state.notifications};
    });
  }

  closeNotificationById(id) {
    let index = this.state.notifications.findIndex((n) => n.id === id);
    if (index !== -1) {
      this.closeNotification(index);
    }
  }

  addNotification(message, tags=[]) {
    this.setState((state, props) => {
      let id = NotificationList._notificationId++;
      state.notifications.push({
        message: message,
        tags: tags,
        id: id
      });

      // Auto-close after 5 seconds.
      window.setTimeout(this.closeNotificationById.bind(this), 5000, id);

      return {notifications: state.notifications};
    });
  }
}

// Unique ID for each notification to use as a React key.
NotificationList._notificationId = 0;

// Only one NotificationList should ever be created.
NotificationList._singleton = null;
