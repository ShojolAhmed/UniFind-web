import { useEffect, useState, useCallback } from 'react'
import ItemCard from '../components/ItemCard'
import { itemsApi, claimsApi, unwrap, apiError } from '../api/client'
import { useToast } from '../context/ToastContext'

export default function DashboardPage() {
  const toast = useToast()
  const [myPosts, setMyPosts] = useState([])
  const [claimedItems, setClaimedItems] = useState([])
  const [pendingClaims, setPendingClaims] = useState([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [posts, claimed, pending] = await Promise.all([
        itemsApi.list({ owner: 'me' }),
        itemsApi.list({ claimed_by: 'me' }),
        claimsApi.mine({ status: 'pending' }),
      ])
      setMyPosts(unwrap(posts))
      setClaimedItems(unwrap(claimed))
      setPendingClaims(unwrap(pending))
    } catch (err) {
      toast.error(apiError(err))
    } finally {
      setLoading(false)
    }
  }, [toast])

  useEffect(() => {
    load()
  }, [load])

  async function handleDelete(item) {
    if (!window.confirm(`Delete "${item.title}"? This cannot be undone.`)) return
    try {
      await itemsApi.remove(item.id)
      toast.success('Item deleted.')
      setMyPosts((prev) => prev.filter((i) => i.id !== item.id))
    } catch (err) {
      toast.error(apiError(err))
    }
  }

  if (loading) {
    return <div className="page-loading">Loading dashboard…</div>
  }

  return (
    <>
      <p className="eyebrow">Your activity</p>
      <h1 className="page-title">Student Dashboard</h1>

      <div className="summary">
        <div className="summary-box">
          <h2>My Posts</h2>
          <p>{myPosts.length}</p>
        </div>
        <div className="summary-box">
          <h2>Pending Claims</h2>
          <p>{pendingClaims.length}</p>
        </div>
        <div className="summary-box">
          <h2>Claimed Items</h2>
          <p>{claimedItems.length}</p>
        </div>
      </div>

      <section className="section">
        <h2 className="section-title">My Posts</h2>
        {myPosts.length ? (
          <div className="board">
            {myPosts.map((item) => (
              <ItemCard key={item.id} item={item} onDelete={handleDelete} />
            ))}
          </div>
        ) : (
          <div className="empty">You have not posted any items yet.</div>
        )}
      </section>

      <section className="section">
        <h2 className="section-title">My Pending Claims</h2>
        {pendingClaims.length ? (
          <div className="item-grid">
            {pendingClaims.map((claim) => (
              <article className="item-card" key={claim.id}>
                {claim.item.image && (
                  <img src={claim.item.image} alt={claim.item.title} loading="lazy" />
                )}
                <div className="item-content">
                  <span className="badge pending">Pending</span>
                  <h3>{claim.item.title}</h3>
                  <p>{claim.item.description}</p>
                  <p>
                    <strong>Location</strong>
                    {claim.item.location}
                  </p>
                  <p>
                    <strong>Owner</strong>
                    {claim.item.owner?.username}
                  </p>
                  <p>
                    <strong>Submitted</strong>
                    {new Date(claim.created_at).toLocaleString()}
                  </p>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="empty">You have no pending claims.</div>
        )}
      </section>

      <section className="section">
        <h2 className="section-title">Claimed Items</h2>
        {claimedItems.length ? (
          <div className="board">
            {claimedItems.map((item) => (
              <ItemCard key={item.id} item={item} />
            ))}
          </div>
        ) : (
          <div className="empty">You have not claimed any items yet.</div>
        )}
      </section>
    </>
  )
}
