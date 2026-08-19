import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import ItemCard from '../components/ItemCard'
import { itemsApi, unwrap, apiError } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

export default function HomePage() {
  const { user } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()

  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [nextUrl, setNextUrl] = useState(null)

  const [title, setTitle] = useState('')
  const [location, setLocation] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  const buildParams = useCallback(() => {
    const params = {}
    if (title.trim()) params.title = title.trim()
    if (location.trim()) params.location = location.trim()
    if (statusFilter !== 'all') params.item_type = statusFilter
    return params
  }, [title, location, statusFilter])

  const fetchItems = useCallback(
    async (params = {}) => {
      setLoading(true)
      try {
        const res = await itemsApi.list(params)
        setItems(unwrap(res))
        setNextUrl(res.data?.next || null)
      } catch (err) {
        toast.error(apiError(err))
      } finally {
        setLoading(false)
      }
    },
    [toast]
  )

  useEffect(() => {
    fetchItems()
  }, [fetchItems])

  function onSearch(e) {
    e.preventDefault()
    fetchItems(buildParams())
  }

  function onClear() {
    setTitle('')
    setLocation('')
    setStatusFilter('all')
    fetchItems()
  }

  async function loadMore() {
    if (!nextUrl) return
    try {
      const res = await itemsApi.byUrl(nextUrl)
      setItems((prev) => [...prev, ...unwrap(res)])
      setNextUrl(res.data?.next || null)
    } catch (err) {
      toast.error(apiError(err))
    }
  }

  async function handleClaim(item) {
    if (!user) {
      navigate('/login')
      return
    }
    if (!window.confirm('Are you sure you want to claim this item?')) return
    try {
      await itemsApi.claim(item.id)
      toast.success('Claim request sent. The owner has been notified.')
      fetchItems(buildParams())
    } catch (err) {
      toast.error(apiError(err))
    }
  }

  async function handleDelete(item) {
    if (!window.confirm(`Delete "${item.title}"? This cannot be undone.`)) return
    try {
      await itemsApi.remove(item.id)
      toast.success('Item deleted.')
      setItems((prev) => prev.filter((i) => i.id !== item.id))
    } catch (err) {
      toast.error(apiError(err))
    }
  }

  return (
    <>
      <div className="topbar">
        <div>
          <p className="eyebrow">Campus lost &amp; found board</p>
          <h2 className="page-title">Browse reported items</h2>
        </div>
      </div>

      <div className="search-container">
        <form className="search-form" onSubmit={onSearch}>
          <input
            name="title"
            placeholder="Search by Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <input
            name="location"
            placeholder="Search by Location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
          <select
            id="statusFilter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All Items</option>
            <option value="Lost">Lost Items</option>
            <option value="Found">Found Items</option>
          </select>
          <button className="btn btn-ink" type="submit">
            Search
          </button>
          <button
            className="btn btn-ghost"
            type="button"
            onClick={onClear}
          >
            Clear
          </button>
        </form>
      </div>

      <section className="board">
        {loading ? (
          <div className="no-items-container">Loading items…</div>
        ) : items.length === 0 ? (
          <div className="no-items-container">
            <p>No lost/found items available</p>
          </div>
        ) : (
          items.map((item) => (
            <ItemCard
              key={item.id}
              item={item}
              onClaim={handleClaim}
              onDelete={handleDelete}
            />
          ))
        )}
      </section>

      {nextUrl && !loading && (
        <div className="load-more">
          <button className="btn btn-ghost" onClick={loadMore}>
            Load more
          </button>
        </div>
      )}
    </>
  )
}
