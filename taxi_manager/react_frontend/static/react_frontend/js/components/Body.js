class AppLayout extends React.Component {
  render() {
    const {
      children
    } = this.props;
    return /*#__PURE__*/React.createElement("body", {
      className: "d-flex flex-column min-vh-100"
    }, children);
  }
}
export default AppLayout;