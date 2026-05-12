const trimTimeZoneFromISO = (value) => {
    if (!value) {
        return ""
    }

    return String(value).slice(0, 16)
}

const getTimeZoneOffset = (value, timeZone) => {
    const probeDate = new Date(`${value}:00Z`)

    const offsetValue = new Intl.DateTimeFormat("en-US", {
        timeZone,
        timeZoneName: "longOffset",
    })
        .formatToParts(probeDate)
        .find((part) => part.type === "timeZoneName")
        ?.value || "GMT+00:00"

    return offsetValue.replace("GMT", "")
}

const addTimeZoneToLocalDateTime = (value, timeZone) => {
    if (!value) {
        return null
    }

    return `${value}:00${getTimeZoneOffset(value, timeZone)}`
}

export {trimTimeZoneFromISO, addTimeZoneToLocalDateTime}