import React from "react"
import { Outlet } from "react-router-dom"

class AppLayout extends React.Component {
  render() {
    return (
      <div className="container py-3">
        <Outlet />
      </div>
    )
  }
}

export default AppLayout