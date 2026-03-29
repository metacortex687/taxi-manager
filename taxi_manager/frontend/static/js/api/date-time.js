const fromISOtoLocaleDateTime = (value) => {
    let local_datetime = ""
    if(value.trim().length !== 0) {
        const date = new Date(value) //Создается в ISO/Z
        local_datetime = new Date(
                date.getTime() - date.getTimezoneOffset() * 60000)
                .toISOString().slice(0, 16)
        
    }
    return local_datetime
}

const fromISOtoLocaleDateTimeString = (value) => {
    return fromISOtoLocaleDateTime(value).replace("-",".").replace("-",".").replace("T", " ")
}



export {fromISOtoLocaleDateTime, fromISOtoLocaleDateTimeString}