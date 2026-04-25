function FormInput({
    id,
    name,
    label,
    value,
    onChange,
    type = "text",
    placeholder = "",
    disabled = false,
    autoComplete,
}) {
    return (
        <div className="mb-3">
            <label htmlFor={id} className="form-label">
                {label}
            </label>
            <input
                id={id}
                name={name}
                type={type}
                className="form-control"
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                disabled={disabled}
                autoComplete={autoComplete}
            />
        </div>
    )
}

export default FormInput