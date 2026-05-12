import { useState } from "react"
import { useParams } from "react-router-dom"

import { uploadFile } from "../api/fetch-data"

import routes from "../routes"

import toast from "react-hot-toast"

function TripsImportPage() {
    const { enterprise_id } = useParams()
    const [file, setFile] = useState(null)
    const [isUploaded, setIsUploaded] = useState(false)

    const handleImport = async () => {
        if (!file) {
            toast.error("Выберите файл архива")
            return
        }

        toast.success(`Начало загрузки "${file.name}"`)

        try {
            await uploadFile(
                routes.trips.import.api(enterprise_id, file.name),
                file,
            )

            toast.success(`Файл "${file.name}" успешно загружен`)
            setIsUploaded(true)
            
        } catch (error) {
            toast.error("Не удалось загрузить файл")
        }
    }

    if (isUploaded) {
        return <p>Файл загружен</p>
    }

    return (
        <div>
            <h1>Импорт поездок</h1>

            <div className="mb-3">
                <label htmlFor="inputUploadFile" className="form-label">
                    Архив
                </label>

                <input
                    id="inputUploadFile"
                    type="file"
                    className="form-control"
                    accept=".zip"
                    onChange={(e) => setFile(e.target.files[0] || null)}
                />
            </div>

            <button
                type="button"
                className="btn btn-primary"
                onClick={handleImport}
            >
                Загрузить
            </button>
        </div>
    )
}

export default TripsImportPage