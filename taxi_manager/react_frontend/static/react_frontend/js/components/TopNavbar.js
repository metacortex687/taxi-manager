import { loadUserInfo, logout } from "../api/users.js";
import AuthContext from "../auth/AuthContest.js";
class TopNavbar extends React.Component {
  static contextType = AuthContext;
  async componentDidMount() {
    const userInfo = await loadUserInfo();
    this.setState({
      userInfo
    });
  }
  handleSubmitLogout = e => {
    e.preventDefault();
    this.context.logout();
  };
  render() {
    const {
      isAuthenticated,
      userInfo
    } = this.context;
    const nameUser = userInfo?.username || "Не авторизован";
    return /*#__PURE__*/React.createElement("nav", {
      className: "navbar navbar-expand-lg navbar-light bg-light px-3"
    }, /*#__PURE__*/React.createElement("ul", {
      className: "navbar-nav d-flex flex-row align-items-center w-100"
    }, /*#__PURE__*/React.createElement("li", {
      className: "nav-item"
    }, /*#__PURE__*/React.createElement("a", {
      href: "#",
      className: "btn btn-secondary btn-lg rounded-1 btn-light border"
    }, "\u041E\u0442\u0447\u0435\u0442\u044B")), /*#__PURE__*/React.createElement("li", {
      className: "nav-item ms-auto"
    }, /*#__PURE__*/React.createElement("form", {
      id: "logoutForm",
      onSubmit: this.handleSubmitLogout
    }, /*#__PURE__*/React.createElement("label", {
      htmlFor: "usernameLabel"
    }, "\u041F\u043E\u043B\u044C\u0437\u043E\u0432\u0430\u0442\u0435\u043B\u044C:"), /*#__PURE__*/React.createElement("label", {
      id: "usernameLabel"
    }, nameUser), isAuthenticated ? /*#__PURE__*/React.createElement("button", {
      type: "submit"
    }, "\u0412\u044B\u0439\u0442\u0438") : null))));
  }
}
export default TopNavbar;