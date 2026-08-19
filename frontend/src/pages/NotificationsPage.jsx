import { useEffect, useState, useCallback } from 'react'
import { notificationsApi, claimsApi, apiError, unwrap } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

function statusLabel(status) {
  if (status === 'approved') return 'Claim Approved'
  if (status === 'rejected') return 'Claim Rejected'
  return null
}

export default function NotificationsPage() {
  const { user } = useAuth()
  const toast = useToast()
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await notificationsApi.list()
      setNotifications(unwrap(res))
    } catch (err) {
      toast.error(apiError(err))
    } finally {
      setLoading(false)
    }
  }, [toast])

  useEffect(() => {
    load()
  }, [load])

  async function approve(claimId) {
    setBusy(claimId)
    try {
      await claimsApi.approve(claimId)
      toast.success('Claim approved.')
      await load()
    } catch (err) {
      toast.error(apiError(err))
    } finally {
      setBusy(null)
    }
  }

  async function reject(claimId) {
    setBusy(claimId)
    try {
      await claimsApi.reject(claimId)
      toast.success('Claim rejected.')
      await load()
    } catch (err) {
      toast.error(apiError(err))
    } finally {
      setBusy(null)
    }
  }

  async function markRead(id) {
    try {
      await notificationsApi.read(id)
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      )
    } catch (err) {
      toast.error(apiError(err))
    }
  }

  async function markAllRead() {
    try {
      await notificationsApi.readAll()
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
      toast.success('All notifications marked as read.')
    } catch (err) {
      toast.error(apiError(err))
    }
  }

  const hasUnread = notifications.some((n) => !n.is_read)

  return (
    <>
      <div className="topbar">
        <div>
          <p className="eyebrow">Claim activity</p>
          <h1 className="page-title">Notifications</h1>
        </div>
        {hasUnread && (
          <button className="btn btn-ghost btn-sm" onClick={markAllRead}>
            Mark all as read
          </button>
        )}
      </div>

      <div className="notification-list">
        {loading ? (
          <div className="empty">Loading…</div>
        ) : notifications.length === 0 ? (
          <div className="empty">You have no notifications.</div>
        ) : (
          notifications.map((n) => {
            const claim = n.claim
            const isOwnerOfClaim =
              claim && claim.item?.owner?.username === user?.username
            const canReview =
              claim && claim.status === 'pending' && isOwnerOfClaim
            const label = claim ? statusLabel(claim.status) : null

            return (
              <div
                key={n.id}
                className={`notification ${n.is_read ? '' : 'unread'}`}
              >
                <div className="message">{n.message}</div>
                <small>{new Date(n.created_at).toLocaleString()}</small>

                {canReview && (
                  <div className="claim-actions">
                    <button
                      className="btn btn-sm btn-success"
                      disabled={busy === claim.id}
                      onClick={() => approve(claim.id)}
                    >
                      Accept Claim
                    </button>
                    <button
                      className="btn btn-sm btn-danger"
                      disabled={busy === claim.id}
                      onClick={() => reject(claim.id)}
                    >
                      Reject Claim
                    </button>
                  </div>
                )}

                {claim && !canReview && label && (
                  <p className="claim-status">{label}</p>
                )}

                {!n.is_read && (
                  <button
                    className="btn btn-sm btn-ghost mark-read"
                    onClick={() => markRead(n.id)}
                  >
                    Mark as read
                  </button>
                )}
              </div>
            )
          })
        )}
      </div>
    </>
  )
}
