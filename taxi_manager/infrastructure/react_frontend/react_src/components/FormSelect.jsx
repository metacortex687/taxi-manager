function FormSelect({
    id,
    name,
    label,
    value,
    onChange,
    placeholder,
    items,
    getOptionLabel,
}) {
    return (
        <div className="mb-3">
            <label htmlFor={id} className="form-label">
                {label}
            </label>
            <select
                id={id}
                name={name}
                className="form-select"
                value={value}
                onChange={onChange}
            >
                <option value="">{placeholder}</option>
                {items.map((item) => (
                    <option key={item.id} value={item.id}>
                        {getOptionLabel(item)}
                    </option>
                ))}
            </select>
        </div>
    )
}

export default FormSelect