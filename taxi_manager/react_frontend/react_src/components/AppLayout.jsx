import React from "react"
import { Outlet } from "react-router-dom"

class AppLayout extends React.Component {
  render() {
    return (
      <div className="d-flex flex-column min-vh-100">
        <Outlet />
      </div>
    )
  }
}

export default AppLayout