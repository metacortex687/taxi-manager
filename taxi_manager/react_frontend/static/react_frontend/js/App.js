import TopNavbar from "./components/TopNavbar.js";
import AppLayout from "./components/AppLayout.js";
import AuthProvider from "./auth/AuthProvider.js";
function App() {
  return /*#__PURE__*/React.createElement(AuthProvider, null, /*#__PURE__*/React.createElement(AppLayout, null, /*#__PURE__*/React.createElement(TopNavbar, null), /*#__PURE__*/React.createElement("h1", null, "Hello world !!!")));
}
export default App;