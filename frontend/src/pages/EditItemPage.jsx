import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { itemsApi, apiError } from '../api/client'
import { useToast } from '../context/ToastContext'

export default function EditItemPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const toast = useToast()

  const [form, setForm] = useState(null)
  const [image, setImage] = useState(null)
  const [preview, setPreview] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    let active = true
    async function load() {
      try {
        const res = await itemsApi.get(id)
        if (!active) return
        if (!res.data.is_owner) {
          toast.error('You are not allowed to edit this item.')
          navigate('/dashboard', { replace: true })
          return
        }
        setForm({
          title: res.data.title,
          item_type: res.data.item_type,
          description: res.data.description,
          location: res.data.location,
          contact: res.data.contact,
        })
        setPreview(res.data.image || '')
      } catch (err) {
        toast.error(apiError(err, 'Item not found.'))
        navigate('/dashboard', { replace: true })
      } finally {
        if (active) setLoading(false)
      }
    }
    load()
    return () => {
      active = false
    }
  }, [id, navigate, toast])

  function update(e) {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  function onImageChange(e) {
    const file = e.target.files?.[0]
    setImage(file || null)
    if (file) setPreview(URL.createObjectURL(file))
  }

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setSubmitting(true)

    const data = new FormData()
    Object.entries(form).forEach(([key, value]) => data.append(key, value))
    if (image) data.append('image', image)

    try {
      await itemsApi.update(id, data)
      toast.success('Changes saved.')
      navigate('/dashboard')
    } catch (err) {
      setError(apiError(err))
    } finally {
      setSubmitting(false)
    }
  }

  if (loading || !form) {
    return <div className="page-loading">Loading…</div>
  }

  return (
    <div className="form-page">
      <div className="form-wrap">
        <p className="eyebrow">Update report</p>
        <h2 className="page-title">Edit Item</h2>

        <div className="card">
          {error && <div className="form-error">{error}</div>}
          <form onSubmit={onSubmit}>
            <div className="field">
              <label htmlFor="title">Title</label>
              <input id="title" name="title" value={form.title} onChange={update} required />
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
              <label htmlFor="image">Replace image (optional)</label>
              <input
                id="image"
                name="image"
                type="file"
                accept="image/*"
                onChange={onImageChange}
              />
            </div>

            {preview && (
              <img
                id="image-preview"
                src={preview}
                alt="Preview"
                style={{ display: 'block' }}
              />
            )}

            <button
              type="submit"
              className="btn btn-ink btn-block"
              disabled={submitting}
            >
              {submitting ? 'Saving…' : 'Save Changes'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
