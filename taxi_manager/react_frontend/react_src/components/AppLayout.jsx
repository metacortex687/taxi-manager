class AppLayout extends React.Component {
    render() {
        const { children } = this.props
        return (
            <div className="d-flex flex-column min-vh-100">
                {children}
            </div>
        )
    }
}

export default AppLayout 