import { loadUserInfo, logout } from "../api/users.js";
import AuthContext from "./AuthContest.js";
class AuthProvider extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      userInfo: null,
      isAuthenticated: null
    };
  }
  async componentDidMount() {
    const token = localStorage.getItem("tokenAuth");
    if (!token) {
      this.setState({
        userInfo: null,
        isAuthenticated: false
      });
      return;
    }
    await this.login(token);
  }
  login = async () => {
    const userInfo = await loadUserInfo();
    const isAuthenticated = userInfo?.username ? true : false;
    this.setState({
      userInfo,
      isAuthenticated
    });
  };
  logout = () => {
    logout();
    this.setState({
      userInfo: null,
      isAuthenticated: false
    });
  };
  render() {
    const value = {
      isAuthenticated: this.state.isAuthenticated,
      userInfo: this.state.userInfo,
      // login: this.login,
      logout: this.logout
    };
    return /*#__PURE__*/React.createElement(AuthContext.Provider, {
      value: value
    }, this.props.children);
  }
}
export default AuthProvider;