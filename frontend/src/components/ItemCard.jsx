import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ItemCard({ item, onClaim, onDelete }) {
  const { user } = useAuth()
  const isOwner = item.is_owner
  const canClaim =
    user && !isOwner && !item.claimed && !item.user_has_pending_claim

  return (
    <div className="ticket" data-status={item.item_type.toLowerCase()}>
      <div className="ticket-media">
        {item.image ? (
          <img src={item.image} alt={item.title} loading="lazy" />
        ) : (
          <div className="ticket-noimg">No image</div>
        )}
        <span className="ticket-status">{item.item_type}</span>
      </div>

      <div className="ticket-seam"></div>

      <div className="ticket-content">
        <span className="ticket-id">TAG-{item.id}</span>

        <h2>{item.title}</h2>
        <p>{item.description}</p>

        <p className="ticket-location">
          <strong>Location</strong>
          {item.location}
        </p>
        <p className="ticket-location">
          <strong>Contact</strong>
          {item.contact}
        </p>

        {item.claimed && <span className="claimed-stamp">CLAIMED</span>}
        {item.claimed && item.claimed_by && (
          <p className="ticket-claim-note">
            Claimed by: {item.claimed_by.username}
          </p>
        )}

        <div className="ticket-actions">
          {canClaim && (
            <button
              className="btn btn-sm btn-success"
              onClick={() => onClaim?.(item)}
            >
              Claim Item
            </button>
          )}

          {user &&
            !isOwner &&
            !item.claimed &&
            item.user_has_pending_claim && (
              <span className="pill pill-pending">Claim pending</span>
            )}

          {isOwner && (
            <>
              <Link className="btn btn-sm btn-ink" to={`/edit/${item.id}`}>
                Edit
              </Link>
              <button
                className="btn btn-sm btn-danger"
                onClick={() => onDelete?.(item)}
              >
                Delete
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
