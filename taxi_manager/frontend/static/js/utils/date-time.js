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


const convert_from_locale_to_iso = (value) => {
    const date = new Date(value) //Создается в ISO/Z
    return date.toISOString()
}

export {fromISOtoLocaleDateTime, fromISOtoLocaleDateTimeString, convert_from_locale_to_iso}