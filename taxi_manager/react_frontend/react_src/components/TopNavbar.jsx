import {loadUserInfo} from "../api/users.js"

class TopNavbar extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            userInfo: null,
        }
    }

    async componentDidMount() {
        const userInfo = await loadUserInfo()
        this.setState({ userInfo })
    }



    render() {
        const {userInfo} = this.state

        const nameUser =  userInfo?.username || "Не авторизован"

        console.log(userInfo) 


        return (
            <nav className="navbar navbar-expand-lg navbar-light bg-light px-3" >
                <ul className="navbar-nav d-flex flex-row align-items-center w-100">
                    <li className="nav-item">
                        <a href="#" className="btn btn-secondary btn-lg rounded-1 btn-light border">
                            Отчеты
                        </a>
                    </li>
                    <li className="nav-item ms-auto">
                        <form id="logoutForm">
                            <label htmlFor="usernameLabel">Пользователь:</label>
                            <label id="usernameLabel">{nameUser}</label>
                            <button type="submit" >Выйти</button>    
                        </form>                        
                    </li>                    
                </ul>
            </nav>
        )
    }
}

export default TopNavbar