function CarMileageReportRow({ row, headers, timeZone }) {
    const formatCellValue = (header) => {
        const value = row[header.name]

        if (header.name === "date" && value) {
            return new Intl.DateTimeFormat("ru-RU", {
                timeZone,
                dateStyle: "short",
            }).format(new Date(value))
        }

        if (header.name === "mileage" && value !== null && value !== undefined && value !== "") {
            return Number(value).toFixed(1)
        }

        return value ?? ""
    }

    return (
        <tr>
            {headers.map((header) => (
                <td key={header.name}>
                    {formatCellValue(header)}
                </td>
            ))}
        </tr>
    )
}

export default CarMileageReportRow