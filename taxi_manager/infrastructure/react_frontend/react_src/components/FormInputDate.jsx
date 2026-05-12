import FormInput from "./FormInput"

function FormInputDate({ id, name, label, value, onChange }) {
    const formatDate = (value) => {
        if (!value) {
            return ""
        }

        return value.slice(0, 10)
    }

    const handleChange = (e) => {
        onChange({
            target: {
                name: e.target.name,
                value: formatDate(e.target.value),
            },
        })
    }
    console.log(value)
    return (
        <FormInput
            id={id}
            name={name}
            label={label}
            type="date"
            value={formatDate(value)}
            onChange={handleChange}
        />
    )
}

export default FormInputDate