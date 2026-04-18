class AppLayout extends React.Component {
    render() {
        const { children } = this.props
        return (
            <body className="d-flex flex-column min-vh-100">
                {children}
            </body>
        )
    }
}

export default AppLayout 