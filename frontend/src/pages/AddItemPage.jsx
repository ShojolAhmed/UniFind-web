import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { itemsApi, apiError } from '../api/client'
import { useToast } from '../context/ToastContext'

const EMPTY = {
  title: '',
  item_type: 'Lost',
  description: '',
  location: '',
  contact: '',
}

export default function AddItemPage() {
  const navigate = useNavigate()
  const toast = useToast()

  const [form, setForm] = useState(EMPTY)
  const [image, setImage] = useState(null)
  const [preview, setPreview] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  function update(e) {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  function onImageChange(e) {
    const file = e.target.files?.[0]
    setImage(file || null)
    setPreview(file ? URL.createObjectURL(file) : '')
  }

  async function onSubmit(e) {
    e.preventDefault()
    setError('')

    if (!image) {
      setError('Please attach an image of the item.')
      return
    }

    setSubmitting(true)
    const data = new FormData()
    Object.entries(form).forEach(([key, value]) => data.append(key, value))
    data.append('image', image)

    try {
      await itemsApi.create(data)
      toast.success('Item posted successfully.')
      navigate('/')
    } catch (err) {
      setError(apiError(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="form-page">
      <div className="form-wrap">
        <p className="eyebrow">New report</p>
        <h2 className="page-title">Add Lost / Found Item</h2>

        <div className="card">
          {error && <div className="form-error">{error}</div>}
          <form onSubmit={onSubmit}>
            <div className="field">
              <label htmlFor="title">Title</label>
              <input
                id="title"
                name="title"
                value={form.title}
                onChange={update}
                required
              />
            </div>

            <div className="field">
              <label htmlFor="item_type">Type</label>
              <select
                id="item_type"
                name="item_type"
                value={form.item_type}
                onChange={update}
              >
                <option value="Lost">Lost</option>
                <option value="Found">Found</option>
              </select>
            </div>

            <div className="field">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                name="description"
                rows={4}
                value={form.description}
                onChange={update}
                required
              />
            </div>

            <div className="field">
              <label htmlFor="location">Location</label>
              <input
                id="location"
                name="location"
                value={form.location}
                onChange={update}
                required
              />
            </div>

            <div className="field">
              <label htmlFor="contact">Contact</label>
              <input
                id="contact"
                name="contact"
                value={form.contact}
                onChange={update}
                required
              />
            </div>

            <div className="field">
              <label htmlFor="image">Image</label>
              <input
                id="image"
                name="image"
                type="file"
                accept="image/*"
                onChange={onImageChange}
                required
              />
            </div>

            {preview && (
              <img id="image-preview" src={preview} alt="Preview" style={{ display: 'block' }} />
            )}

            <button
              type="submit"
              className="btn btn-success btn-block"
              disabled={submitting}
            >
              {submitting ? 'Submitting…' : 'Submit Item'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
